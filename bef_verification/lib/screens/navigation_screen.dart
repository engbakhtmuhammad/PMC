import 'package:flutter/material.dart';
import '../utils/constants.dart';
import 'home_screen.dart';
import 'saved_forms_screen.dart';
import 'profile_screen.dart';

class NavigationScreen extends StatefulWidget {
  const NavigationScreen({super.key});

  @override
  State<NavigationScreen> createState() => _NavigationScreenState();
}

class _NavigationScreenState extends State<NavigationScreen> {
  int _index = 0;
  late final List<Widget> _pages = [
    const HomeScreen(),
    const SavedFormsScreen(),
    const ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _pages[_index],
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: whiteColor,
          boxShadow: [
            BoxShadow(
              color: Colors.black12,
              blurRadius: 8,
              offset: Offset(0, -2),
            ),
          ],
        ),
        child: NavigationBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          selectedIndex: _index,
          onDestinationSelected: (i) => setState(() => _index = i),
          labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
          destinations: [
            NavigationDestination(
              icon: Icon(Icons.home_outlined, color: _index == 0 ? primaryColor : Colors.grey.shade600),
              selectedIcon: Icon(Icons.home, color: primaryColor),
              label: 'Home',
            ),
            NavigationDestination(
              icon: Icon(Icons.school_outlined, color: _index == 1 ? primaryColor : Colors.grey.shade600),
              selectedIcon: Icon(Icons.school, color: primaryColor),
              label: 'Visited Schools',
            ),
            NavigationDestination(
              icon: Icon(Icons.person_outline, color: _index == 2 ? primaryColor : Colors.grey.shade600),
              selectedIcon: Icon(Icons.person, color: primaryColor),
              label: 'Profile',
            ),
          ],
        ),
      ),
    );
  }
} 