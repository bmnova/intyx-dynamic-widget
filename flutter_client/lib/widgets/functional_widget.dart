import 'package:flutter/material.dart';

class FunctionalWidget extends StatelessWidget {
  final String title;
  final String? text;
  final List<FunctionalAction> actions;
  final void Function(String action)? onAction;

  const FunctionalWidget({
    super.key,
    required this.title,
    this.text,
    required this.actions,
    this.onAction,
  });

  factory FunctionalWidget.fromJson(
    Map<String, dynamic> params, {
    void Function(String url)? onAction,
  }) {
    final rawActions = params['actions'] as List<dynamic>? ?? [];
    return FunctionalWidget(
      title: params['title'] as String? ?? '',
      text: params['text'] as String?,
      actions: rawActions
          .map((e) => FunctionalAction.fromJson(e as Map<String, dynamic>))
          .toList(),
      onAction: onAction,
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(title, style: theme.textTheme.titleMedium),
            if (text != null && text!.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(
                text!,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: actions.map((a) {
                switch (a.style) {
                  case 'secondary':
                    return OutlinedButton(
                      onPressed: () => onAction?.call(a.action),
                      child: Text(a.label),
                    );
                  case 'text':
                    return TextButton(
                      onPressed: () => onAction?.call(a.action),
                      child: Text(a.label),
                    );
                  default: // primary
                    return FilledButton(
                      onPressed: () => onAction?.call(a.action),
                      child: Text(a.label),
                    );
                }
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }
}

class FunctionalAction {
  final String label;
  final String action;
  final String style;

  const FunctionalAction({
    required this.label,
    required this.action,
    this.style = 'primary',
  });

  factory FunctionalAction.fromJson(Map<String, dynamic> json) {
    return FunctionalAction(
      label: json['label'] as String? ?? '',
      action: (json['action'] ?? json['url'] ?? '') as String,
      style: json['style'] as String? ?? 'primary',
    );
  }
}
