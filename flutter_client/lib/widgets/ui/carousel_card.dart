import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

class CarouselCard extends StatefulWidget {
  final String? title;
  final String? text;
  final List<CarouselItem> items;
  final void Function(String url)? onItemTap;

  const CarouselCard({
    super.key,
    this.title,
    this.text,
    required this.items,
    this.onItemTap,
  });

  factory CarouselCard.fromJson(Map<String, dynamic> params) {
    final rawItems = params['items'] as List<dynamic>? ?? [];
    return CarouselCard(
      title: params['title'] as String?,
      text: params['text'] as String?,
      items: rawItems
          .map((e) => CarouselItem.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  @override
  State<CarouselCard> createState() => _CarouselCardState();
}

class _CarouselCardState extends State<CarouselCard> {
  int _currentPage = 0;
  late final PageController _pageController;

  @override
  void initState() {
    super.initState();
    _pageController = PageController(viewportFraction: 0.85);
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (widget.items.isEmpty) return const SizedBox.shrink();

    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          if (widget.title != null && widget.title!.isNotEmpty)
            Padding(
              padding: EdgeInsets.fromLTRB(16, 16, 16, widget.text != null ? 4 : 8),
              child: Text(widget.title!, style: theme.textTheme.titleMedium),
            ),
          if (widget.text != null && widget.text!.isNotEmpty)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
              child: Text(
                widget.text!,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ),
          SizedBox(
            height: 200,
            child: PageView.builder(
              controller: _pageController,
              itemCount: widget.items.length,
              onPageChanged: (i) => setState(() => _currentPage = i),
              itemBuilder: (context, index) {
                final item = widget.items[index];
                return Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: GestureDetector(
                    onTap: item.linkUrl != null
                        ? () => widget.onItemTap?.call(item.linkUrl!)
                        : null,
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: Stack(
                        fit: StackFit.expand,
                        children: [
                          CachedNetworkImage(
                            imageUrl: item.imageUrl,
                            fit: item.imageFit,
                            placeholder: (_, __) => Container(
                              color: theme.colorScheme.surfaceContainerHighest,
                            ),
                            errorWidget: (_, __, ___) => Container(
                              color: theme.colorScheme.surfaceContainerHighest,
                              child: const Icon(Icons.broken_image_outlined),
                            ),
                          ),
                          if (item.title != null || item.description != null)
                            Positioned(
                              left: 0,
                              right: 0,
                              bottom: 0,
                              child: Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  gradient: LinearGradient(
                                    begin: Alignment.topCenter,
                                    end: Alignment.bottomCenter,
                                    colors: [
                                      Colors.transparent,
                                      Colors.black.withValues(alpha: 0.7),
                                    ],
                                  ),
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    if (item.title != null)
                                      Text(
                                        item.title!,
                                        style: theme.textTheme.titleSmall?.copyWith(color: Colors.white),
                                      ),
                                    if (item.description != null)
                                      Text(
                                        item.description!,
                                        style: theme.textTheme.bodySmall?.copyWith(color: Colors.white70),
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                  ],
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          if (widget.items.length > 1)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 12),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(widget.items.length, (i) {
                  return Container(
                    width: 8,
                    height: 8,
                    margin: const EdgeInsets.symmetric(horizontal: 3),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: i == _currentPage
                          ? theme.colorScheme.primary
                          : theme.colorScheme.surfaceContainerHighest,
                    ),
                  );
                }),
              ),
            ),
        ],
      ),
    );
  }
}

class CarouselItem {
  final String imageUrl;
  final BoxFit imageFit;
  final String? title;
  final String? description;
  final String? linkUrl;

  const CarouselItem({
    required this.imageUrl,
    this.imageFit = BoxFit.cover,
    this.title,
    this.description,
    this.linkUrl,
  });

  factory CarouselItem.fromJson(Map<String, dynamic> json) {
    return CarouselItem(
      imageUrl: json['image_url'] as String? ?? '',
      imageFit: _parseFit(json['image_fit']),
      title: json['title'] as String?,
      description: (json['description'] ?? json['text']) as String?,
      linkUrl: json['link_url'] as String?,
    );
  }

  static BoxFit _parseFit(dynamic value) {
    switch (value) {
      case 'contain':
        return BoxFit.contain;
      case 'fill':
        return BoxFit.fill;
      default:
        return BoxFit.cover;
    }
  }
}
