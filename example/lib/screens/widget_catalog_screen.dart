import 'package:flutter/material.dart';
import 'package:intyx_dynamic_widget/intyx_dynamic_widget.dart';

/// Tüm widget tiplerini tek tek örnekleriyle gösteren katalog sayfası.
class WidgetCatalogScreen extends StatelessWidget {
  const WidgetCatalogScreen({super.key});

  static final Map<String, Map<String, dynamic>> catalogByType = {
    'banner': {
      'widgets': [
        {
          'id': 'cat_banner',
          'type': 'banner',
          'params': {
            'text': 'Hoş geldiniz! Bugün harika bir gün.',
            'emoji': '👋',
            'style': 'gradient',
          },
          'common': {'priority': 1},
        },
      ],
    },
    'title_subtitle_image': {
      'widgets': [
        {
          'id': 'cat_tsi',
          'type': 'title_subtitle_image',
          'params': {
            'title': 'Katalog Örneği',
            'subtitle': 'Başlık, alt metin ve görsel kart.',
            'image_url': 'https://picsum.photos/400/200',
          },
          'common': {'priority': 1},
        },
      ],
    },
    'clickable_image_link': {
      'widgets': [
        {
          'id': 'cat_click',
          'type': 'clickable_image_link',
          'params': {
            'image_url': 'https://picsum.photos/600/300',
            'link_url': 'app://demo',
            'caption': 'Tıklanabilir görsel',
          },
          'common': {'priority': 1},
        },
      ],
    },
    'hero_image': {
      'widgets': [
        {
          'id': 'cat_hero',
          'type': 'hero_image',
          'params': {
            'title': 'Hero Kart',
            'image_url': 'https://picsum.photos/seed/hero2/800/400',
            'button_text': 'Keşfet',
            'button_action': 'app://hero',
          },
          'common': {'priority': 1, 'layout': {'aspect_ratio': 1.78}},
        },
      ],
    },
    'icon_text_action': {
      'widgets': [
        {
          'id': 'cat_icon',
          'type': 'icon_text_action',
          'params': {
            'icon': 'star',
            'title': 'Öne Çıkan',
            'description': 'Aksiyon butonu ile kart.',
            'action_text': 'Devam',
            'action_url': 'app://action',
          },
          'common': {'priority': 1},
        },
      ],
    },
    'countdown_banner': {
      'widgets': [
        {
          'id': 'cat_cd',
          'type': 'countdown_banner',
          'params': {
            'title': 'Kampanya Bitişi',
            'end_time': DateTime.now()
                .add(const Duration(hours: 1, minutes: 15))
                .toIso8601String(),
            'button_text': 'Katıl',
            'button_action': 'app://campaign',
          },
          'common': {'priority': 1},
        },
      ],
    },
    'carousel': {
      'widgets': [
        {
          'id': 'cat_carousel',
          'type': 'carousel',
          'params': {
            'title': 'Öne Çıkan Ürünler',
            'items': [
              {
                'image_url': 'https://picsum.photos/300/200?random=1',
                'title': 'Ürün 1',
                'description': 'Açıklama',
              },
              {
                'image_url': 'https://picsum.photos/300/200?random=2',
                'title': 'Ürün 2',
                'description': 'Açıklama',
              },
            ],
          },
          'common': {'priority': 1},
        },
      ],
    },
    'promotional': {
      'widgets': [
        {
          'id': 'cat_promo',
          'type': 'promotional',
          'params': {
            'title': 'İndirim Kampanyası',
            'description': 'Seçili ürünlerde %30\'a varan indirim.',
            'image_url': 'https://picsum.photos/800/400',
            'badge_text': '%30',
            'action_url': 'app://promo',
          },
          'common': {'priority': 1},
        },
      ],
    },
    'contextual': {
      'widgets': [
        {
          'id': 'cat_ctx',
          'type': 'contextual',
          'params': {
            'title': 'Bağlamsal Bilgi',
            'content': 'Hava, konum veya kullanıcıya özel içerik.',
            'icon': 'info',
            'source': 'Demo',
          },
          'common': {'priority': 1},
        },
      ],
    },
    'informational': {
      'widgets': [
        {
          'id': 'cat_info',
          'type': 'informational',
          'params': {
            'title': 'Bilgi Duyurusu',
            'message': 'Bu bir bilgilendirme mesajıdır.',
            'severity': 'info',
          },
          'common': {'priority': 1},
        },
      ],
    },
    'functional': {
      'widgets': [
        {
          'id': 'cat_func',
          'type': 'functional',
          'params': {
            'title': 'Hızlı İşlemler',
            'actions': [
              {'label': 'Evet', 'action': 'yes', 'style': 'primary'},
              {'label': 'Hayır', 'action': 'no', 'style': 'secondary'},
            ],
          },
          'common': {'priority': 1},
        },
      ],
    },
    'rating': {
      'widgets': [
        {
          'id': 'cat_rating',
          'type': 'rating',
          'params': {
            'title': 'Deneyiminizi puanlayın',
            'subtitle': '1-5 yıldız seçin',
            'max_stars': 5,
          },
          'common': {'priority': 1},
        },
      ],
    },
    'poll': {
      'widgets': [
        {
          'id': 'cat_poll',
          'type': 'poll',
          'params': {
            'question': 'En çok hangi widget tipini kullanırsınız?',
            'options': ['Banner', 'Carousel', 'Countdown', 'Hero'],
          },
          'common': {'priority': 1},
        },
      ],
    },
    'social_proof': {
      'widgets': [
        {
          'id': 'cat_social',
          'type': 'social_proof',
          'params': {
            'title': 'Kullanıcı Yorumları',
            'quote': 'Çok kullanışlı bir paket, kurulumu kolay.',
            'author': 'Ayşe K.',
          },
          'common': {'priority': 1},
        },
      ],
    },
    'progress': {
      'widgets': [
        {
          'id': 'cat_progress',
          'type': 'progress',
          'params': {
            'title': 'Profil tamamlanma',
            'progress': 0.75,
            'progress_label': '%75',
          },
          'common': {'priority': 1},
        },
      ],
    },
    'profile': {
      'widgets': [
        {
          'id': 'cat_profile',
          'type': 'profile',
          'params': {
            'name': 'Demo Kullanıcı',
            'subtitle': 'Örnek profil kartı',
            'avatar_url': 'https://picsum.photos/100',
          },
          'common': {'priority': 1},
        },
      ],
    },
  };

  @override
  Widget build(BuildContext context) {
    final types = catalogByType.keys.toList()..sort();
    return Scaffold(
      appBar: AppBar(
        title: const Text('Widget Kataloğu'),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
        itemCount: types.length,
        itemBuilder: (context, index) {
          final type = types[index];
          final responseJson = catalogByType[type]!;
          return Card(
            margin: const EdgeInsets.only(bottom: 20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
                  child: Text(
                    type,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Theme.of(context).colorScheme.primary,
                        ),
                  ),
                ),
                DynamicWidgetContainer(
                  responseJson: responseJson,
                  colorScheme: Theme.of(context).colorScheme,
                  onDismiss: (_) {},
                  onAction: (id, action) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Aksiyon: $action')),
                    );
                  },
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
