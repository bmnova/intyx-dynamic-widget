import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

class ClickableImageLinkCard extends StatelessWidget {
  final String title;
  final String imageUrl;
  final String linkUrl;
  final String? linkText;
  final void Function(String url)? onLinkTap;

  const ClickableImageLinkCard({
    super.key,
    required this.title,
    required this.imageUrl,
    required this.linkUrl,
    this.linkText,
    this.onLinkTap,
  });

  factory ClickableImageLinkCard.fromJson(
    Map<String, dynamic> params, {
    void Function(String url)? onAction,
  }) {
    return ClickableImageLinkCard(
      title: params['title'] as String? ?? '',
      imageUrl: params['image_url'] as String? ?? '',
      linkUrl: params['link_url'] as String? ?? '',
      linkText: params['link_text'] as String?,
      onLinkTap: onAction,
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 12),
            child: Text(title, style: theme.textTheme.titleMedium),
          ),
          if (imageUrl.isNotEmpty)
            GestureDetector(
              onTap: () => onLinkTap?.call(linkUrl),
              child: AspectRatio(
                aspectRatio: 16 / 9,
                child: CachedNetworkImage(
                  imageUrl: imageUrl,
                  fit: BoxFit.cover,
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
            ),
          InkWell(
            onTap: () => onLinkTap?.call(linkUrl),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Icon(Icons.link, size: 18, color: theme.colorScheme.primary),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      linkText ?? linkUrl,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.primary,
                        decoration: TextDecoration.underline,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
