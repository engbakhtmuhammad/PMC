import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'screens/register_screen.dart';
import 'screens/login_screen.dart';
import 'screens/bef_form_screen.dart';
import 'screens/saved_forms_screen.dart';
import 'utils/constants.dart';
import 'package:google_fonts/google_fonts.dart';
import 'screens/navigation_screen.dart';
import 'screens/bef_wizard_screen.dart';


Future<void> initializeFirebase() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
}

void main() async {
  await initializeFirebase();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'BEF Verification',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: primaryColor),
        useMaterial3: true,
        textTheme: GoogleFonts.senTextTheme(),
      ),
      initialRoute: '/login',
      routes: {
        '/login': (context) => const LoginScreen(),
        '/register': (context) => const RegisterScreen(),
        '/bef_form': (context) => const BEFFormScreen(),
  '/saved_forms': (context) => SavedFormsScreen(),
        '/nav': (context) => const NavigationScreen(),
        '/bef_wizard': (context) => const BEFWizardScreen(),
      },
    );
  }
}
