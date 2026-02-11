import 'dart:async';

import 'package:flutter/material.dart';

class CountdownBannerCard extends StatefulWidget {
  final String title;
  final DateTime endTime;
  final String? buttonText;
  final String? buttonAction;
  final void Function(String action)? onAction;

  const CountdownBannerCard({
    super.key,
    required this.title,
    required this.endTime,
    this.buttonText,
    this.buttonAction,
    this.onAction,
  });

  factory CountdownBannerCard.fromJson(Map<String, dynamic> params) {
    return CountdownBannerCard(
      title: params['title'] as String? ?? '',
      endTime: DateTime.tryParse(params['end_time'] as String? ?? '') ??
          DateTime.now().add(const Duration(hours: 1)),
      buttonText: params['button_text'] as String?,
      buttonAction: params['button_action'] as String?,
    );
  }

  @override
  State<CountdownBannerCard> createState() => _CountdownBannerCardState();
}

class _CountdownBannerCardState extends State<CountdownBannerCard> {
  late Timer _timer;
  Duration _remaining = Duration.zero;

  @override
  void initState() {
    super.initState();
    _updateRemaining();
    _timer = Timer.periodic(const Duration(seconds: 1), (_) => _updateRemaining());
  }

  void _updateRemaining() {
    final now = DateTime.now();
    setState(() {
      _remaining = widget.endTime.isAfter(now)
          ? widget.endTime.difference(now)
          : Duration.zero;
    });
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  String _formatDuration(Duration d) {
    final days = d.inDays;
    final hours = d.inHours.remainder(24).toString().padLeft(2, '0');
    final minutes = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = d.inSeconds.remainder(60).toString().padLeft(2, '0');

    if (days > 0) return '$days gun $hours:$minutes:$seconds';
    return '$hours:$minutes:$seconds';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isExpired = _remaining == Duration.zero;

    return Card(
      color: theme.colorScheme.primaryContainer,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              isExpired ? '00:00:00' : _formatDuration(_remaining),
              style: theme.textTheme.headlineMedium?.copyWith(
                color: theme.colorScheme.onPrimaryContainer,
                fontWeight: FontWeight.bold,
                fontFeatures: const [FontFeature.tabularFigures()],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              widget.title,
              style: theme.textTheme.titleMedium?.copyWith(
                color: theme.colorScheme.onPrimaryContainer,
              ),
              textAlign: TextAlign.center,
            ),
            if (widget.buttonText != null && !isExpired) ...[
              const SizedBox(height: 16),
              FilledButton(
                onPressed: widget.buttonAction != null
                    ? () => widget.onAction?.call(widget.buttonAction!)
                    : null,
                child: Text(widget.buttonText!),
              ),
            ],
            if (isExpired) ...[
              const SizedBox(height: 8),
              Text(
                'Sure doldu',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onPrimaryContainer.withValues(alpha: 0.7),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
