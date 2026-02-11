import 'package:flutter/material.dart';

/// Progress/goal card — "3/5 gorev tamamlandi" tarzinda.
class ProgressCard extends StatelessWidget {
  final String title;
  final String? subtitle;
  final double progress; // 0.0 - 1.0
  final String? progressLabel;
  final String? actionText;
  final String? actionUrl;

  const ProgressCard({
    super.key,
    required this.title,
    this.subtitle,
    required this.progress,
    this.progressLabel,
    this.actionText,
    this.actionUrl,
  });

  factory ProgressCard.fromJson(Map<String, dynamic> params) {
    return ProgressCard(
      title: params['title'] as String? ?? '',
      subtitle: params['subtitle'] as String?,
      progress: (params['progress'] as num?)?.toDouble() ?? 0.0,
      progressLabel: params['progress_label'] as String?,
      actionText: params['action_text'] as String?,
      actionUrl: params['action_url'] as String?,
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final pct = (progress * 100).round();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(title, style: theme.textTheme.titleMedium),
                ),
                Text(
                  '$pct%',
                  style: theme.textTheme.titleMedium?.copyWith(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ],
            ),
            if (subtitle != null) ...[
              const SizedBox(height: 4),
              Text(
                subtitle!,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
            const SizedBox(height: 16),
            ClipRRect(
              borderRadius: BorderRadius.circular(6),
              child: LinearProgressIndicator(
                value: progress.clamp(0.0, 1.0),
                minHeight: 8,
                backgroundColor: theme.colorScheme.surfaceContainerHighest,
                valueColor: AlwaysStoppedAnimation(theme.colorScheme.primary),
              ),
            ),
            if (progressLabel != null) ...[
              const SizedBox(height: 8),
              Text(
                progressLabel!,
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.outline,
                ),
              ),
            ],
            if (actionText != null) ...[
              const SizedBox(height: 12),
              Align(
                alignment: Alignment.centerRight,
                child: TextButton(
                  onPressed: () {},
                  child: Text(actionText!),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
