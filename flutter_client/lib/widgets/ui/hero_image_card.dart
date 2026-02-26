import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

class HeroImageCard extends StatelessWidget {
  final String title;
  final String? text;
  final String imageUrl;
  final String? buttonText;
  final String? buttonAction;
  final void Function(String action)? onAction;

  const HeroImageCard({
    super.key,
    required this.title,
    this.text,
    required this.imageUrl,
    this.buttonText,
    this.buttonAction,
    this.onAction,
  });

  factory HeroImageCard.fromJson(
    Map<String, dynamic> params, {
    void Function(String url)? onAction,
  }) {
    return HeroImageCard(
      title: params['title'] as String? ?? '',
      text: params['text'] as String?,
      imageUrl: params['image_url'] as String? ?? '',
      buttonText: params['button_text'] as String?,
      buttonAction: params['button_action'] as String?,
      onAction: onAction,
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      clipBehavior: Clip.antiAlias,
      child: Stack(
        children: [
          if (imageUrl.isNotEmpty)
            AspectRatio(
              aspectRatio: 16 / 9,
              child: CachedNetworkImage(
                imageUrl: imageUrl,
                fit: BoxFit.cover,
                placeholder: (_, __) => Container(
                  color: theme.colorScheme.surfaceContainerHighest,
                ),
                errorWidget: (_, __, ___) => Container(
                  color: theme.colorScheme.surfaceContainerHighest,
                  child: const Icon(Icons.broken_image_outlined, size: 48),
                ),
              ),
            ),
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.transparent,
                    Colors.black.withValues(alpha: 0.7),
                  ],
                  stops: const [0.3, 1.0],
                ),
              ),
            ),
          ),
          Positioned(
            left: 16,
            right: 16,
            bottom: 16,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  title,
                  style: theme.textTheme.headlineSmall?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (text != null && text!.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    text!,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: Colors.white.withValues(alpha: 0.85),
                    ),
                  ),
                ],
                if (buttonText != null && buttonText!.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  FilledButton(
                    onPressed: buttonAction != null
                        ? () => onAction?.call(buttonAction!)
                        : null,
                    child: Text(buttonText!),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}
