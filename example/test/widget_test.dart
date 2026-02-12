import 'package:flutter_test/flutter_test.dart';
import 'package:intyx_example/main.dart';

void main() {
  testWidgets('Uygulama açılıyor ve ana sayfa görünüyor', (WidgetTester tester) async {
    await tester.pumpWidget(const IntyxExampleApp());
    await tester.pumpAndSettle();

    expect(find.text('Intyx Örnek Uygulama'), findsOneWidget);
    expect(find.text('Widget Akışı'), findsOneWidget);
  });
}
