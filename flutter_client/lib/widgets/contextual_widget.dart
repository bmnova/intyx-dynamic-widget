import 'package:flutter/material.dart';

class ContextualWidget extends StatelessWidget {
  final String title;
  final String content;
  final String? icon;
  final String? source;
  final VoidCallback? onTap;

  const ContextualWidget({
    super.key,
    required this.title,
    required this.content,
    this.icon,
    this.source,
    this.onTap,
  });

  factory ContextualWidget.fromJson(Map<String, dynamic> params) {
    return ContextualWidget(
      title: params['title'] as String? ?? '',
      content: params['content'] as String? ?? '',
      icon: params['icon'] as String?,
      source: params['source'] as String?,
    );
  }

  IconData _resolveIcon() {
    const iconMap = <String, IconData>{
      'info': Icons.info_outline,
      'warning': Icons.warning_amber,
      'weather': Icons.cloud_outlined,
      'star': Icons.star_outline,
      'location': Icons.location_on_outlined,
      'calendar': Icons.calendar_today_outlined,
      'clock': Icons.access_time_outlined,
    };
    return iconMap[icon] ?? Icons.widgets_outlined;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: theme.colorScheme.secondaryContainer,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  _resolveIcon(),
                  color: theme.colorScheme.onSecondaryContainer,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: theme.textTheme.titleSmall),
                    const SizedBox(height: 4),
                    Text(
                      content,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    if (source != null) ...[
                      const SizedBox(height: 8),
                      Text(
                        source!,
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: theme.colorScheme.outline,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
