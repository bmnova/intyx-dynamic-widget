import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

class PromotionalWidget extends StatelessWidget {
  final String title;
  final String? description;
  final String? imageUrl;
  final String? badgeText;
  final String? actionUrl;
  final void Function(String url)? onAction;

  const PromotionalWidget({
    super.key,
    required this.title,
    this.description,
    this.imageUrl,
    this.badgeText,
    this.actionUrl,
    this.onAction,
  });

  factory PromotionalWidget.fromJson(Map<String, dynamic> params) {
    return PromotionalWidget(
      title: params['title'] as String? ?? '',
      description: params['description'] as String?,
      imageUrl: params['image_url'] as String?,
      badgeText: params['badge_text'] as String?,
      actionUrl: params['action_url'] as String?,
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: actionUrl != null ? () => onAction?.call(actionUrl!) : null,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisSize: MainAxisSize.min,
          children: [
            if (imageUrl != null && imageUrl!.isNotEmpty)
              Stack(
                children: [
                  AspectRatio(
                    aspectRatio: 2,
                    child: CachedNetworkImage(
                      imageUrl: imageUrl!,
                      fit: BoxFit.cover,
                      placeholder: (_, __) => Container(
                        color: theme.colorScheme.primaryContainer,
                      ),
                      errorWidget: (_, __, ___) => Container(
                        color: theme.colorScheme.primaryContainer,
                        child: const Icon(Icons.campaign_outlined, size: 48),
                      ),
                    ),
                  ),
                  if (badgeText != null)
                    Positioned(
                      top: 12,
                      right: 12,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.error,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          badgeText!,
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: theme.colorScheme.onError,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (badgeText != null && (imageUrl == null || imageUrl!.isEmpty))
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.error,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          badgeText!,
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: theme.colorScheme.onError,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                  Text(title, style: theme.textTheme.titleMedium),
                  if (description != null && description!.isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Text(
                      description!,
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
