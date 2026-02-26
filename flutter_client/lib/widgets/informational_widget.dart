import 'package:flutter/material.dart';

class InformationalWidget extends StatelessWidget {
  final String title;
  final String message;
  final String severity;
  final VoidCallback? onTap;

  const InformationalWidget({
    super.key,
    required this.title,
    required this.message,
    this.severity = 'info',
    this.onTap,
  });

  factory InformationalWidget.fromJson(
    Map<String, dynamic> params, {
    void Function(String url)? onAction,
  }) {
    final actionUrl = params['action_url'] as String?;
    return InformationalWidget(
      title: params['title'] as String? ?? '',
      message: ((params['message'] ?? params['text']) as String?) ?? '',
      severity: params['severity'] as String? ?? 'info',
      onTap: actionUrl != null && onAction != null
          ? () => onAction(actionUrl)
          : null,
    );
  }

  ({Color bg, Color fg, IconData icon}) _severityStyle(ThemeData theme) {
    switch (severity) {
      case 'warning':
        return (
          bg: Colors.orange.shade50,
          fg: Colors.orange.shade800,
          icon: Icons.warning_amber_rounded,
        );
      case 'error':
        return (
          bg: Colors.red.shade50,
          fg: Colors.red.shade800,
          icon: Icons.error_outline_rounded,
        );
      case 'success':
        return (
          bg: Colors.green.shade50,
          fg: Colors.green.shade800,
          icon: Icons.check_circle_outline_rounded,
        );
      default: // info
        return (
          bg: Colors.blue.shade50,
          fg: Colors.blue.shade800,
          icon: Icons.info_outline_rounded,
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final style = _severityStyle(theme);

    return Card(
      color: style.bg,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(style.icon, color: style.fg, size: 24),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: theme.textTheme.titleSmall?.copyWith(color: style.fg),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      message,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: style.fg.withValues(alpha: 0.8),
                      ),
                    ),
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
