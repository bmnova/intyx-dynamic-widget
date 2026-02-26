import 'package:flutter/material.dart';

class IconTextActionCard extends StatelessWidget {
  final String iconName;
  final String title;
  final String? description;
  final String? actionText;
  final String? actionUrl;
  final void Function(String url)? onAction;

  const IconTextActionCard({
    super.key,
    required this.iconName,
    required this.title,
    this.description,
    this.actionText,
    this.actionUrl,
    this.onAction,
  });

  factory IconTextActionCard.fromJson(
    Map<String, dynamic> params, {
    void Function(String url)? onAction,
  }) {
    return IconTextActionCard(
      iconName: params['icon'] as String? ?? 'info',
      title: params['title'] as String? ?? '',
      description: params['description'] as String?,
      actionText: params['action_text'] as String?,
      actionUrl: params['action_url'] as String?,
      onAction: onAction,
    );
  }

  IconData _resolveIcon() {
    const iconMap = <String, IconData>{
      'info': Icons.info_outline,
      'warning': Icons.warning_amber,
      'error': Icons.error_outline,
      'success': Icons.check_circle_outline,
      'star': Icons.star_outline,
      'favorite': Icons.favorite_outline,
      'notification': Icons.notifications_outlined,
      'settings': Icons.settings_outlined,
      'shopping': Icons.shopping_cart_outlined,
      'delivery': Icons.local_shipping_outlined,
      'location': Icons.location_on_outlined,
      'calendar': Icons.calendar_today_outlined,
      'clock': Icons.access_time_outlined,
      'weather': Icons.cloud_outlined,
      'offer': Icons.local_offer_outlined,
      'gift': Icons.card_giftcard_outlined,
      'campaign': Icons.campaign_outlined,
      'target': Icons.gps_fixed,
    };
    return iconMap[iconName] ?? Icons.widgets_outlined;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: InkWell(
        onTap: actionUrl != null ? () => onAction?.call(actionUrl!) : null,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: theme.colorScheme.primaryContainer,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  _resolveIcon(),
                  color: theme.colorScheme.onPrimaryContainer,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(title, style: theme.textTheme.titleSmall),
                    if (description != null && description!.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        description!,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ],
                ),
              ),
              if (actionText != null) ...[
                const SizedBox(width: 8),
                TextButton(
                  onPressed: actionUrl != null
                      ? () => onAction?.call(actionUrl!)
                      : null,
                  child: Text(actionText!),
                ),
              ] else if (actionUrl != null) ...[
                const SizedBox(width: 8),
                Icon(
                  Icons.chevron_right,
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
