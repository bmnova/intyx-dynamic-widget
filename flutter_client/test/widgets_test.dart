import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intyx_dynamic_widget/intyx_dynamic_widget.dart';

void main() {
  setUp(() {
    WidgetRegistry.clear();
    registerDefaultWidgets();
  });

  group('WidgetRegistry', () {
    test('registers all default widget types', () {
      expect(WidgetRegistry.hasType('title_subtitle_image'), true);
      expect(WidgetRegistry.hasType('clickable_image_link'), true);
      expect(WidgetRegistry.hasType('hero_image'), true);
      expect(WidgetRegistry.hasType('icon_text_action'), true);
      expect(WidgetRegistry.hasType('countdown_banner'), true);
      expect(WidgetRegistry.hasType('carousel'), true);
      expect(WidgetRegistry.hasType('promotional'), true);
      expect(WidgetRegistry.hasType('contextual'), true);
      expect(WidgetRegistry.hasType('informational'), true);
      expect(WidgetRegistry.hasType('functional'), true);
    });

    test('build returns null for unknown type', () {
      expect(WidgetRegistry.build('nonexistent', {}), isNull);
    });

    test('build returns widget for known type', () {
      final widget = WidgetRegistry.build('informational', {
        'title': 'Test',
        'message': 'Hello',
      });
      expect(widget, isNotNull);
      expect(widget, isA<InformationalWidget>());
    });

    test('clear removes all registrations', () {
      WidgetRegistry.clear();
      expect(WidgetRegistry.registeredTypes, isEmpty);
    });
  });

  group('WidgetResolver', () {
    test('resolve creates widgets from JSON', () {
      final widgets = WidgetResolver.resolve({
        'widgets': [
          {
            'id': 'w1',
            'type': 'informational',
            'params': {'title': 'Test', 'message': 'Hello'},
          },
        ],
      });
      expect(widgets.length, 1);
    });

    test('resolve skips unknown types', () {
      final widgets = WidgetResolver.resolve({
        'widgets': [
          {
            'id': 'w1',
            'type': 'unknown_type',
            'params': {},
          },
        ],
      });
      expect(widgets, isEmpty);
    });

    test('resolveSingle returns null for unknown type', () {
      final entry = WidgetEntry.fromJson({
        'id': 'w1',
        'type': 'unknown',
        'params': {},
      });
      expect(WidgetResolver.resolveSingle(entry), isNull);
    });
  });

  group('Widget rendering', () {
    testWidgets('InformationalWidget renders title and message', (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: InformationalWidget(title: 'Alert', message: 'Test message'),
        ),
      ));

      expect(find.text('Alert'), findsOneWidget);
      expect(find.text('Test message'), findsOneWidget);
    });

    testWidgets('IconTextActionCard renders icon and title', (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: IconTextActionCard(
            iconName: 'star',
            title: 'Starred Item',
            description: 'A description',
          ),
        ),
      ));

      expect(find.text('Starred Item'), findsOneWidget);
      expect(find.text('A description'), findsOneWidget);
    });

    testWidgets('FunctionalWidget renders buttons', (tester) async {
      String? tappedAction;
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: FunctionalWidget(
            title: 'Choose',
            actions: const [
              FunctionalAction(label: 'Option A', action: 'a'),
              FunctionalAction(label: 'Option B', action: 'b', style: 'secondary'),
            ],
            onAction: (action) => tappedAction = action,
          ),
        ),
      ));

      expect(find.text('Choose'), findsOneWidget);
      expect(find.text('Option A'), findsOneWidget);
      expect(find.text('Option B'), findsOneWidget);

      await tester.tap(find.text('Option A'));
      expect(tappedAction, 'a');
    });

    testWidgets('CountdownBannerCard renders timer', (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: CountdownBannerCard(
            title: 'Sale Ending',
            endTime: DateTime.now().add(const Duration(hours: 1)),
            buttonText: 'Shop Now',
          ),
        ),
      ));

      expect(find.text('Sale Ending'), findsOneWidget);
      expect(find.text('Shop Now'), findsOneWidget);
    });

    testWidgets('DynamicWidgetContainer renders from JSON', (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: DynamicWidgetContainer(
            responseJson: {
              'widgets': [
                {
                  'id': 'w1',
                  'type': 'informational',
                  'params': {'title': 'Info', 'message': 'Message'},
                },
              ],
            },
          ),
        ),
      ));

      expect(find.text('Info'), findsOneWidget);
      expect(find.text('Message'), findsOneWidget);
    });

    testWidgets('ResponsiveWidgetWrapper applies expand by default', (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: ResponsiveWidgetWrapper(
            child: Container(height: 50, color: Colors.blue),
          ),
        ),
      ));

      final sizedBox = tester.widget<SizedBox>(find.byType(SizedBox).first);
      expect(sizedBox.width, double.infinity);
    });
  });
}
