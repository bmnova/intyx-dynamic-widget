import 'package:flutter/material.dart';

/// Social proof card — "1.234 kisi bu urunu aldi" / testimonial tarzinda.
class SocialProofCard extends StatelessWidget {
  final String title;
  final String? subtitle;
  final String? metric;
  final String? metricLabel;
  final String? avatarUrl;
  final String? quote;
  final String? author;

  const SocialProofCard({
    super.key,
    required this.title,
    this.subtitle,
    this.metric,
    this.metricLabel,
    this.avatarUrl,
    this.quote,
    this.author,
  });

  factory SocialProofCard.fromJson(Map<String, dynamic> params) {
    return SocialProofCard(
      title: params['title'] as String? ?? '',
      subtitle: params['subtitle'] as String?,
      metric: params['metric'] as String?,
      metricLabel: params['metric_label'] as String?,
      avatarUrl: params['avatar_url'] as String?,
      quote: params['quote'] as String?,
      author: params['author'] as String?,
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            // Metric row
            if (metric != null)
              Row(
                children: [
                  Text(
                    metric!,
                    style: theme.textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                      color: theme.colorScheme.primary,
                    ),
                  ),
                  if (metricLabel != null) ...[
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        metricLabel!,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            if (metric != null) const SizedBox(height: 12),

            Text(title, style: theme.textTheme.titleSmall),
            if (subtitle != null) ...[
              const SizedBox(height: 4),
              Text(
                subtitle!,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],

            // Quote / testimonial
            if (quote != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '"$quote"',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                    if (author != null) ...[
                      const SizedBox(height: 8),
                      Text(
                        '— $author',
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: theme.colorScheme.outline,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
