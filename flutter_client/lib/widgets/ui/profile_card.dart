import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

/// Profile / user spotlight card.
class ProfileCard extends StatelessWidget {
  final String name;
  final String? avatarUrl;
  final String? title;
  final String? subtitle;
  final String? text;
  final String? actionText;
  final String? actionUrl;

  const ProfileCard({
    super.key,
    required this.name,
    this.avatarUrl,
    this.title,
    this.subtitle,
    this.text,
    this.actionText,
    this.actionUrl,
  });

  factory ProfileCard.fromJson(Map<String, dynamic> params) {
    return ProfileCard(
      name: params['name'] as String? ?? '',
      avatarUrl: params['avatar_url'] as String?,
      title: params['title'] as String?,
      subtitle: (params['subtitle'] ?? params['text']) as String?,
      text: params['subtitle'] != null ? params['text'] as String? : null,
      actionText: params['action_text'] as String?,
      actionUrl: params['action_url'] as String?,
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            CircleAvatar(
              radius: 28,
              backgroundColor: theme.colorScheme.primaryContainer,
              backgroundImage: avatarUrl != null && avatarUrl!.isNotEmpty
                  ? CachedNetworkImageProvider(avatarUrl!)
                  : null,
              child: avatarUrl == null || avatarUrl!.isEmpty
                  ? Text(
                      name.isNotEmpty ? name[0].toUpperCase() : '?',
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w700,
                        color: theme.colorScheme.onPrimaryContainer,
                      ),
                    )
                  : null,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(name, style: theme.textTheme.titleMedium),
                  if (title != null)
                    Text(
                      title!,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  if (subtitle != null)
                    Text(
                      subtitle!,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.outline,
                      ),
                    ),
                  if (text != null)
                    Text(
                      text!,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.outline,
                      ),
                    ),
                ],
              ),
            ),
            if (actionText != null)
              FilledButton.tonal(
                onPressed: () {},
                child: Text(actionText!),
              ),
          ],
        ),
      ),
    );
  }
}
