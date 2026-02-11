import 'package:flutter/material.dart';
import 'package:intyx_dynamic_widget/intyx_dynamic_widget.dart';

void main() {
  registerDefaultWidgets();
  runApp(const ExampleApp());
}

class ExampleApp extends StatelessWidget {
  const ExampleApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Intyx Dynamic Widget Demo',
      theme: ThemeData(
        colorSchemeSeed: Colors.indigo,
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        colorSchemeSeed: Colors.indigo,
        brightness: Brightness.dark,
        useMaterial3: true,
      ),
      home: const DemoPage(),
    );
  }
}

class DemoPage extends StatelessWidget {
  const DemoPage({super.key});

  // Simulated agent response
  Map<String, dynamic> get _mockAgentResponse => {
    "widgets": [
      {
        "id": "w_weather",
        "type": "contextual",
        "params": {
          "title": "Istanbul'da Bugun",
          "content": "Parcali bulutlu, 18°C - Semsiyeni almayı unutma!",
          "icon": "weather",
          "source": "OpenWeather"
        },
        "common": {"priority": 30, "dismissible": true}
      },
      {
        "id": "w_promo",
        "type": "promotional",
        "params": {
          "title": "Yaz Indirimi Basladi!",
          "description": "Secili urunlerde buyuk firsatlar sizi bekliyor.",
          "image_url": "https://picsum.photos/800/400",
          "badge_text": "%50 Indirim",
          "action_url": "app://deals"
        },
        "common": {"priority": 20}
      },
      {
        "id": "w_hero",
        "type": "hero_image",
        "params": {
          "title": "Yeni Koleksiyon",
          "image_url": "https://picsum.photos/seed/hero/800/450",
          "button_text": "Kesfet",
          "button_action": "app://collection"
        },
        "common": {
          "priority": 15,
          "layout": {"aspect_ratio": 1.78}
        }
      },
      {
        "id": "w_info",
        "type": "informational",
        "params": {
          "title": "Sistem Bakimi",
          "message": "Yarin 02:00-04:00 arasi planli bakim yapilacaktir.",
          "severity": "warning"
        },
        "common": {"priority": 10}
      },
      {
        "id": "w_action",
        "type": "icon_text_action",
        "params": {
          "icon": "gift",
          "title": "Gunun Firsati",
          "description": "Ozel indirim kodunuzu kullanin",
          "action_text": "Kullan",
          "action_url": "app://coupon"
        },
        "common": {"priority": 5}
      },
      {
        "id": "w_countdown",
        "type": "countdown_banner",
        "params": {
          "title": "Flash Sale Bitis Suresi",
          "end_time": DateTime.now().add(const Duration(hours: 2, minutes: 30)).toIso8601String(),
          "button_text": "Firsatlari Gor",
          "button_action": "app://flash-sale"
        },
        "common": {"priority": 25}
      },
      {
        "id": "w_func",
        "type": "functional",
        "params": {
          "title": "Bildirim Tercihleri",
          "actions": [
            {"label": "Hepsini Ac", "action": "notifications_on", "style": "primary"},
            {"label": "Sadece Onemli", "action": "notifications_important", "style": "secondary"},
            {"label": "Kapat", "action": "notifications_off", "style": "text"}
          ]
        },
        "common": {"priority": 1}
      }
    ]
  };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Dynamic Widget Demo')),
      body: DynamicWidgetContainer(
        responseJson: _mockAgentResponse,
        onDismiss: (widgetId) {
          debugPrint('Widget dismissed: $widgetId');
        },
        onAction: (widgetId, action) {
          debugPrint('Widget action: $widgetId -> $action');
        },
      ),
    );
  }
}
