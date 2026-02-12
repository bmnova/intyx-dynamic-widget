import 'package:flutter/material.dart';
import 'package:intyx_dynamic_widget/intyx_dynamic_widget.dart';

import 'widget_catalog_screen.dart';

/// Tek bir widget tipi seçip canlı önizleme yapılan oynatma alanı.
class WidgetPlaygroundScreen extends StatefulWidget {
  const WidgetPlaygroundScreen({super.key});

  @override
  State<WidgetPlaygroundScreen> createState() => _WidgetPlaygroundScreenState();
}

class _WidgetPlaygroundScreenState extends State<WidgetPlaygroundScreen> {
  String? _selectedType;

  Map<String, dynamic> _buildResponseForType(String type) {
    final catalog = WidgetCatalogScreen.catalogByType;
    if (catalog.containsKey(type)) {
      return catalog[type]!;
    }
    return {'widgets': []};
  }

  @override
  Widget build(BuildContext context) {
    final types = WidgetCatalogScreen.catalogByType.keys.toList()..sort();
    return Scaffold(
      appBar: AppBar(
        title: const Text('Widget Oynatma Alanı'),
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Widget tipi seçin',
                      style: Theme.of(context).textTheme.titleSmall,
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      initialValue: _selectedType,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        contentPadding: EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 8,
                        ),
                      ),
                      hint: const Text('Tip seçin...'),
                      items: types
                          .map((t) => DropdownMenuItem(
                                value: t,
                                child: Text(t),
                              ))
                          .toList(),
                      onChanged: (value) {
                        setState(() => _selectedType = value);
                      },
                    ),
                  ],
                ),
              ),
            ),
          ),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16),
            child: Text(
              'Önizleme',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: _selectedType == null
                ? Center(
                    child: Text(
                      'Yukarıdan bir widget tipi seçin',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: Theme.of(context).colorScheme.onSurfaceVariant,
                          ),
                    ),
                  )
               : SingleChildScrollView(
                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
                    child: DynamicWidgetContainer(
                      responseJson: _buildResponseForType(_selectedType!),
                      colorScheme: Theme.of(context).colorScheme,
                      onDismiss: (_) {},
                      onAction: (id, action) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Aksiyon: $action')),
                        );
                      },
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}
