import 'package:flutter/material.dart';
import 'package:intyx_dynamic_widget/intyx_dynamic_widget.dart';

class WidgetFeedScreen extends StatelessWidget {
  const WidgetFeedScreen({super.key});

  static Map<String, dynamic> get _mockAgentResponse => {
        'widgets': [
          {
            'id': 'w_weather',
            'type': 'contextual',
            'params': {
              'title': "Istanbul'da Bugün",
              'content':
                  'Parçalı bulutlu, 18°C - Şemsiyeni almayı unutma!',
              'icon': 'weather',
              'source': 'OpenWeather',
            },
            'common': {'priority': 30, 'dismissible': true},
          },
          {
            'id': 'w_promo',
            'type': 'promotional',
            'params': {
              'title': 'Yaz İndirimi Başladı!',
              'description':
                  'Seçili ürünlerde büyük fırsatlar sizi bekliyor.',
              'image_url': 'https://picsum.photos/800/400',
              'badge_text': '%50 İndirim',
              'action_url': 'app://deals',
            },
            'common': {'priority': 20},
          },
          {
            'id': 'w_hero',
            'type': 'hero_image',
            'params': {
              'title': 'Yeni Koleksiyon',
              'image_url': 'https://picsum.photos/seed/hero/800/450',
              'button_text': 'Keşfet',
              'button_action': 'app://collection',
            },
            'common': {
              'priority': 15,
              'layout': {'aspect_ratio': 1.78},
            },
          },
          {
            'id': 'w_info',
            'type': 'informational',
            'params': {
              'title': 'Sistem Bakımı',
              'message':
                  'Yarın 02:00-04:00 arası planlı bakım yapılacaktır.',
              'severity': 'warning',
            },
            'common': {'priority': 10},
          },
          {
            'id': 'w_action',
            'type': 'icon_text_action',
            'params': {
              'icon': 'gift',
              'title': 'Günün Fırsatı',
              'description': 'Özel indirim kodunuzu kullanın',
              'action_text': 'Kullan',
              'action_url': 'app://coupon',
            },
            'common': {'priority': 5},
          },
          {
            'id': 'w_countdown',
            'type': 'countdown_banner',
            'params': {
              'title': 'Flash Sale Bitiş Süresi',
              'end_time': DateTime.now()
                  .add(const Duration(hours: 2, minutes: 30))
                  .toIso8601String(),
              'button_text': 'Fırsatları Gör',
              'button_action': 'app://flash-sale',
            },
            'common': {'priority': 25},
          },
          {
            'id': 'w_func',
            'type': 'functional',
            'params': {
              'title': 'Bildirim Tercihleri',
              'actions': [
                {
                  'label': 'Hepsini Aç',
                  'action': 'notifications_on',
                  'style': 'primary',
                },
                {
                  'label': 'Sadece Önemli',
                  'action': 'notifications_important',
                  'style': 'secondary',
                },
                {
                  'label': 'Kapat',
                  'action': 'notifications_off',
                  'style': 'text',
                },
              ],
            },
            'common': {'priority': 1},
          },
        ],
      };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Widget Akışı'),
      ),
      body: DynamicWidgetContainer(
        responseJson: _mockAgentResponse,
        colorScheme: Theme.of(context).colorScheme,
        onDismiss: (widgetId) {
          debugPrint('Widget kapatıldı: $widgetId');
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Kapatıldı: $widgetId')),
          );
        },
        onAction: (widgetId, action) {
          debugPrint('Aksiyon: $widgetId -> $action');
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Aksiyon: $action')),
          );
        },
      ),
    );
  }
}
