import 'package:flutter/material.dart';

/// Paket hakkında bilgi ve kullanım örnekleri.
class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Paket Hakkında'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'intyx_dynamic_widget',
                    style: theme.textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'AI tarafından belirlenen, JSON ile yapılandırılan dinamik widget sistemi. '
                    '15+ hazır UI bileşeni: banner, carousel, hero, countdown, poll, rating, '
                    'profile, progress, social proof ve daha fazlası.',
                    style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Kullanım',
            style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 8),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: theme.brightness == Brightness.dark
                  ? theme.colorScheme.surfaceContainerHigh
                  : theme.colorScheme.surfaceContainerLow,
              borderRadius: BorderRadius.circular(12),
            ),
            child: SelectableText(
              _usageSnippet,
              style: theme.textTheme.bodySmall?.copyWith(
                    fontFamily: 'monospace',
                    fontSize: 12,
                  ),
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'Sayfalar',
            style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 8),
          _LinkTile(
            icon: Icons.dashboard_customize,
            title: 'Widget Akışı',
            subtitle: 'Örnek widget listesi (feed)',
            onTap: () => Navigator.of(context).pushNamed('/feed'),
          ),
          _LinkTile(
            icon: Icons.view_list,
            title: 'Widget Kataloğu',
            subtitle: 'Tüm tipler tek tek',
            onTap: () => Navigator.of(context).pushNamed('/catalog'),
          ),
          _LinkTile(
            icon: Icons.science,
            title: 'Widget Oynatma Alanı',
            subtitle: 'Tek tip seçip önizleme',
            onTap: () => Navigator.of(context).pushNamed('/playground'),
          ),
          const SizedBox(height: 24),
          Center(
            child: Text(
              'pub.dev/packages/intyx_dynamic_widget',
              style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.primary,
                  ),
            ),
          ),
        ],
      ),
    );
  }

  static const String _usageSnippet = '''
// 1. Başlangıçta kayıt
void main() {
  registerDefaultWidgets();
  runApp(MyApp());
}

// 2. JSON ile container
DynamicWidgetContainer(
  responseJson: agentResponse,  // { "widgets": [...] }
  colorScheme: Theme.of(context).colorScheme,
  onAction: (id, action) => ...,
  onDismiss: (id) => ...,
);
''';
}

class _LinkTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _LinkTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon),
        title: Text(title),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.arrow_forward_ios, size: 14),
        onTap: onTap,
      ),
    );
  }
}
