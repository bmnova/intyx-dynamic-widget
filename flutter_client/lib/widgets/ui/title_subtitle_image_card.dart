import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

class TitleSubtitleImageCard extends StatelessWidget {
  final String title;
  final String? subtitle;
  final String imageUrl;
  final BoxFit imageFit;
  final VoidCallback? onTap;

  const TitleSubtitleImageCard({
    super.key,
    required this.title,
    this.subtitle,
    required this.imageUrl,
    this.imageFit = BoxFit.cover,
    this.onTap,
  });

  factory TitleSubtitleImageCard.fromJson(Map<String, dynamic> params) {
    return TitleSubtitleImageCard(
      title: params['title'] as String? ?? '',
      subtitle: params['subtitle'] as String?,
      imageUrl: params['image_url'] as String? ?? '',
      imageFit: _parseFit(params['image_fit']),
    );
  }

  static BoxFit _parseFit(dynamic value) {
    switch (value) {
      case 'contain':
        return BoxFit.contain;
      case 'fill':
        return BoxFit.fill;
      default:
        return BoxFit.cover;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return GestureDetector(
      onTap: onTap,
      child: Card(
        clipBehavior: Clip.antiAlias,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisSize: MainAxisSize.min,
          children: [
            if (imageUrl.isNotEmpty)
              AspectRatio(
                aspectRatio: 16 / 9,
                child: CachedNetworkImage(
                  imageUrl: imageUrl,
                  fit: imageFit,
                  placeholder: (_, __) => Container(
                    color: theme.colorScheme.surfaceContainerHighest,
                    child: const Center(child: CircularProgressIndicator(strokeWidth: 2)),
                  ),
                  errorWidget: (_, __, ___) => Container(
                    color: theme.colorScheme.surfaceContainerHighest,
                    child: const Icon(Icons.broken_image_outlined),
                  ),
                ),
              ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: theme.textTheme.titleMedium),
                  if (subtitle != null && subtitle!.isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Text(
                      subtitle!,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
