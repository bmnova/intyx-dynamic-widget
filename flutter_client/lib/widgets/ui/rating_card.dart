import 'package:flutter/material.dart';

/// Star-rating request card — "Bu deneyimi nasil buldunuz?" tarzinda.
class RatingCard extends StatefulWidget {
  final String title;
  final String? subtitle;
  final int maxStars;
  final void Function(int rating)? onRate;

  const RatingCard({
    super.key,
    required this.title,
    this.subtitle,
    this.maxStars = 5,
    this.onRate,
  });

  factory RatingCard.fromJson(Map<String, dynamic> params) {
    return RatingCard(
      title: params['title'] as String? ?? '',
      subtitle: params['subtitle'] as String?,
      maxStars: params['max_stars'] as int? ?? 5,
    );
  }

  @override
  State<RatingCard> createState() => _RatingCardState();
}

class _RatingCardState extends State<RatingCard> {
  int _selected = 0;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(widget.title, style: theme.textTheme.titleMedium),
            if (widget.subtitle != null) ...[
              const SizedBox(height: 4),
              Text(
                widget.subtitle!,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(widget.maxStars, (i) {
                final filled = i < _selected;
                return GestureDetector(
                  onTap: () {
                    setState(() => _selected = i + 1);
                    widget.onRate?.call(i + 1);
                  },
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: Icon(
                      filled ? Icons.star_rounded : Icons.star_outline_rounded,
                      size: 36,
                      color: filled
                          ? theme.colorScheme.primary
                          : theme.colorScheme.outlineVariant,
                    ),
                  ),
                );
              }),
            ),
          ],
        ),
      ),
    );
  }
}
