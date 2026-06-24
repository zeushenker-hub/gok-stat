import 'package:flutter/material.dart';
import 'chores_screen.dart';
import 'purchases_screen.dart';
import 'events_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _index = 0;

  final _pages = const [
    ChoresScreen(),
    PurchasesScreen(),
    EventsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.cleaning_services_outlined), label: 'Дела'),
          NavigationDestination(icon: Icon(Icons.shopping_cart_outlined), label: 'Покупки'),
          NavigationDestination(icon: Icon(Icons.event_outlined), label: 'События'),
        ],
      ),
    );
  }
}
