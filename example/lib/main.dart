import 'package:flutter/material.dart';
import 'package:intyx_dynamic_widget/intyx_dynamic_widget.dart';

import 'screens/about_screen.dart';
import 'screens/home_screen.dart';
import 'screens/widget_catalog_screen.dart';
import 'screens/widget_feed_screen.dart';
import 'screens/widget_playground_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  registerDefaultWidgets();
  runApp(const IntyxExampleApp());
}

class IntyxExampleApp extends StatelessWidget {
  const IntyxExampleApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Intyx Dynamic Widget Örnek',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: Colors.deepPurple,
        useMaterial3: true,
        appBarTheme: const AppBarTheme(centerTitle: true),
      ),
      darkTheme: ThemeData(
        colorSchemeSeed: Colors.deepPurple,
        brightness: Brightness.dark,
        useMaterial3: true,
      ),
      home: const HomeScreen(),
      routes: {
        '/feed': (context) => const WidgetFeedScreen(),
        '/catalog': (context) => const WidgetCatalogScreen(),
        '/playground': (context) => const WidgetPlaygroundScreen(),
        '/about': (context) => const AboutScreen(),
      },
    );
  }
}
