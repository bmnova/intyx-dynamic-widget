import 'package:flutter/material.dart';

/// Simple text banner — ozel gun kutlamasi, duyuru, motivasyon tarzinda.
class BannerCard extends StatelessWidget {
  final String text;
  final String? emoji;
  final String? actionText;
  final String? actionUrl;
  final String style; // 'default', 'gradient', 'outlined'

  const BannerCard({
    super.key,
    required this.text,
    this.emoji,
    this.actionText,
    this.actionUrl,
    this.style = 'default',
  });

  factory BannerCard.fromJson(Map<String, dynamic> params) {
    return BannerCard(
      text: params['text'] as String? ?? '',
      emoji: params['emoji'] as String?,
      actionText: params['action_text'] as String?,
      actionUrl: params['action_url'] as String?,
      style: params['style'] as String? ?? 'default',
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    BoxDecoration decoration;
    Color textColor;

    switch (style) {
      case 'gradient':
        decoration = BoxDecoration(
          borderRadius: BorderRadius.circular(14),
          gradient: LinearGradient(
            colors: [
              theme.colorScheme.primary,
              theme.colorScheme.secondary,
            ],
          ),
        );
        textColor = theme.colorScheme.onPrimary;
        break;
      case 'outlined':
        decoration = BoxDecoration(
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: theme.colorScheme.outlineVariant),
        );
        textColor = theme.colorScheme.onSurface;
        break;
      default:
        decoration = BoxDecoration(
          borderRadius: BorderRadius.circular(14),
          color: theme.colorScheme.primaryContainer,
        );
        textColor = theme.colorScheme.onPrimaryContainer;
    }

    return Container(
      decoration: decoration,
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
      child: Row(
        children: [
          if (emoji != null) ...[
            Text(emoji!, style: const TextStyle(fontSize: 28)),
            const SizedBox(width: 16),
          ],
          Expanded(
            child: Text(
              text,
              style: theme.textTheme.titleSmall?.copyWith(
                color: textColor,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          if (actionText != null)
            TextButton(
              onPressed: () {},
              style: TextButton.styleFrom(foregroundColor: textColor),
              child: Text(actionText!),
            ),
        ],
      ),
    );
  }
}
