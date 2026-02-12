import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Intyx Örnek Uygulama'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          const SizedBox(height: 24),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Dinamik Widget Sistemi',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'AI tarafından belirlenen widget\'lar JSON yanıtıyla gelir ve bu paket ile otomatik render edilir.',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Theme.of(context).colorScheme.onSurfaceVariant,
                        ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          ListTile(
            leading: const Icon(Icons.dashboard_customize),
            title: const Text('Widget Akışı'),
            subtitle: const Text('Örnek widget listesini görüntüle'),
            trailing: const Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () => Navigator.of(context).pushNamed('/feed'),
          ),
          ListTile(
            leading: const Icon(Icons.view_list),
            title: const Text('Widget Kataloğu'),
            subtitle: const Text('Tüm widget tiplerini tek tek incele'),
            trailing: const Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () => Navigator.of(context).pushNamed('/catalog'),
          ),
          ListTile(
            leading: const Icon(Icons.science),
            title: const Text('Widget Oynatma Alanı'),
            subtitle: const Text('Tek tip seçip canlı önizleme'),
            trailing: const Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () => Navigator.of(context).pushNamed('/playground'),
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text('Paket Hakkında'),
            subtitle: const Text('Kullanım ve pub.dev linki'),
            trailing: const Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () => Navigator.of(context).pushNamed('/about'),
          ),
        ],
      ),
    );
  }
}
