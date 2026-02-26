import 'package:flutter/material.dart';

/// Simple poll/survey card with tappable options.
class PollCard extends StatefulWidget {
  final String question;
  final List<String> options;
  final void Function(int index, String option)? onVote;

  const PollCard({
    super.key,
    required this.question,
    required this.options,
    this.onVote,
  });

  factory PollCard.fromJson(Map<String, dynamic> params) {
    final rawOptions = params['options'] as List<dynamic>? ?? [];
    return PollCard(
      question: ((params['question'] ?? params['title'] ?? params['text']) as String?) ?? '',
      options: rawOptions.map((e) => e.toString()).toList(),
    );
  }

  @override
  State<PollCard> createState() => _PollCardState();
}

class _PollCardState extends State<PollCard> {
  int? _selected;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(widget.question, style: theme.textTheme.titleMedium),
            const SizedBox(height: 16),
            ...widget.options.asMap().entries.map((entry) {
              final i = entry.key;
              final option = entry.value;
              final selected = _selected == i;
              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Material(
                  color: selected
                      ? theme.colorScheme.primaryContainer
                      : theme.colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(10),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(10),
                    onTap: _selected == null
                        ? () {
                            setState(() => _selected = i);
                            widget.onVote?.call(i, option);
                          }
                        : null,
                    child: Padding(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 14,
                      ),
                      child: Row(
                        children: [
                          Icon(
                            selected
                                ? Icons.check_circle_rounded
                                : Icons.circle_outlined,
                            size: 20,
                            color: selected
                                ? theme.colorScheme.primary
                                : theme.colorScheme.outline,
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              option,
                              style: theme.textTheme.bodyMedium?.copyWith(
                                fontWeight:
                                    selected ? FontWeight.w600 : FontWeight.normal,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}
