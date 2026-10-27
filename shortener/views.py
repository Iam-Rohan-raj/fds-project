import qrcode
import qrcode.image.svg
import io
import base64
from PIL import Image

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import URL, Click
from .forms import URLForm


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def detect_device(user_agent):
    if not user_agent:
        return 'Unknown'
    ua = user_agent.lower()
    if any(m in ua for m in ['mobile', 'android', 'iphone', 'ipod']):
        return 'Mobile'
    elif any(m in ua for m in ['tablet', 'ipad']):
        return 'Tablet'
    return 'Desktop'


def home(request):
    """Homepage with URL shortening form and recent links."""
    form = URLForm()
    recent_urls = URL.objects.filter(is_active=True).order_by('-created_at')[:8]

    total_urls = URL.objects.count()
    total_clicks = URL.objects.aggregate(total=Sum('click_count'))['total'] or 0
    active_urls = URL.objects.filter(is_active=True).count()

    context = {
        'form': form,
        'recent_urls': recent_urls,
        'total_urls': total_urls,
        'total_clicks': total_clicks,
        'active_urls': active_urls,
    }
    return render(request, 'shortener/home.html', context)


def shorten_url(request):
    """Handle URL shortening POST request."""
    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            url_obj = form.save()
            short_url = request.build_absolute_uri(f'/{url_obj.get_short_identifier()}/')
            messages.success(request, f'URL shortened successfully!')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'short_url': short_url,
                    'short_code': url_obj.get_short_identifier(),
                    'original_url': url_obj.original_url,
                    'id': url_obj.id,
                })
            return redirect('url_detail', pk=url_obj.pk)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            # Re-render home with errors
            recent_urls = URL.objects.filter(is_active=True).order_by('-created_at')[:8]
            total_urls = URL.objects.count()
            total_clicks = URL.objects.aggregate(total=Sum('click_count'))['total'] or 0
            active_urls = URL.objects.filter(is_active=True).count()
            return render(request, 'shortener/home.html', {
                'form': form,
                'recent_urls': recent_urls,
                'total_urls': total_urls,
                'total_clicks': total_clicks,
                'active_urls': active_urls,
            })
    return redirect('home')


def redirect_url(request, short_code):
    """Redirect short URL to original URL and track click."""
    url_obj = URL.objects.filter(
        short_code=short_code, is_active=True
    ).first() or URL.objects.filter(
        custom_alias=short_code, is_active=True
    ).first()

    if not url_obj:
        raise Http404("Short URL not found.")

    if url_obj.is_expired():
        return render(request, 'shortener/expired.html', {'url': url_obj}, status=410)

    # Track the click
    Click.objects.create(
        url=url_obj,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        referer=request.META.get('HTTP_REFERER', ''),
        device_type=detect_device(request.META.get('HTTP_USER_AGENT', '')),
    )
    url_obj.increment_clicks()

    return redirect(url_obj.original_url)


def url_detail(request, pk):
    """Show URL detail with analytics."""
    url_obj = get_object_or_404(URL, pk=pk)
    short_url = request.build_absolute_uri(f'/{url_obj.get_short_identifier()}/')

    # Click analytics (last 7 days)
    seven_days_ago = timezone.now() - timezone.timedelta(days=7)
    daily_clicks = (
        Click.objects.filter(url=url_obj, clicked_at__gte=seven_days_ago)
        .annotate(date=TruncDate('clicked_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    # Device breakdown
    device_stats = (
        Click.objects.filter(url=url_obj)
        .values('device_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    recent_clicks = url_obj.clicks.all()[:10]

    context = {
        'url': url_obj,
        'short_url': short_url,
        'daily_clicks': list(daily_clicks),
        'device_stats': list(device_stats),
        'recent_clicks': recent_clicks,
    }
    return render(request, 'shortener/url_detail.html', context)


def all_urls(request):
    """List all shortened URLs with search/filter."""
    query = request.GET.get('q', '')
    urls = URL.objects.all()
    if query:
        urls = urls.filter(original_url__icontains=query) | urls.filter(
            short_code__icontains=query
        ) | urls.filter(custom_alias__icontains=query) | urls.filter(
            title__icontains=query
        )

    total_clicks = URL.objects.aggregate(total=Sum('click_count'))['total'] or 0

    context = {
        'urls': urls,
        'query': query,
        'total_clicks': total_clicks,
    }
    return render(request, 'shortener/all_urls.html', context)


def generate_qr(request, pk):
    """Generate QR code for a short URL and return as PNG."""
    url_obj = get_object_or_404(URL, pk=pk)
    short_url = request.build_absolute_uri(f'/{url_obj.get_short_identifier()}/')

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(short_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#6C63FF", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="qr_{url_obj.get_short_identifier()}.png"'
    return response


def qr_preview(request, pk):
    """Return QR code as base64 for inline preview."""
    url_obj = get_object_or_404(URL, pk=pk)
    short_url = request.build_absolute_uri(f'/{url_obj.get_short_identifier()}/')

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=3,
    )
    qr.add_data(short_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#6C63FF", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    encoded = base64.b64encode(buffer.getvalue()).decode()

    return JsonResponse({'qr_data': f'data:image/png;base64,{encoded}'})


def toggle_url(request, pk):
    """Toggle URL active/inactive status."""
    url_obj = get_object_or_404(URL, pk=pk)
    url_obj.is_active = not url_obj.is_active
    url_obj.save(update_fields=['is_active'])
    status = 'activated' if url_obj.is_active else 'deactivated'
    messages.success(request, f'URL {status} successfully.')
    return redirect('all_urls')


def delete_url(request, pk):
    """Delete a shortened URL."""
    url_obj = get_object_or_404(URL, pk=pk)
    if request.method == 'POST':
        url_obj.delete()
        messages.success(request, 'URL deleted successfully.')
        return redirect('all_urls')
    return render(request, 'shortener/confirm_delete.html', {'url': url_obj})
