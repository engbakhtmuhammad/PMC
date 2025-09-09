import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../utils/constants.dart';
import '../utils/style.dart';
import '../widgets/input_field.dart';
import '../widgets/custom_btn.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final AuthService _authService = AuthService();

  String email = '';
  String password = '';
  bool isLoading = false;
  String error = '';

  void _login() async {
    if (_formKey.currentState!.validate()) {
      setState(() { isLoading = true; error = ''; });
      try {
        await _authService.signInWithEmailAndPassword(email, password);
        setState(() { isLoading = false; });
        Navigator.pushReplacementNamed(context, '/nav');
      } catch (e) {
        setState(() { error = e.toString(); isLoading = false; });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold( 
      backgroundColor: backgroundColor,
      appBar: AppBar(
        title: Text('Login', style: titleTextStyle(color: whiteColor)),
        backgroundColor: primaryColor,
        elevation: 0,
      ),
      body: Center(
        child: SingleChildScrollView(
          child: Padding(
            padding: EdgeInsets.all(defaultPadding),
            child: Card(
              elevation: 2,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(containerRoundCorner)),
              child: Padding(
                padding: EdgeInsets.symmetric(horizontal: defaultPadding, vertical: 32),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text('Welcome Back', style: titleTextStyle(size: 24, color: primaryColor, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
                      SizedBox(height: 24),
                      Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Padding(
                              padding: const EdgeInsets.only(bottom: 6),
                              child: Text('Email', style: subTitleTextStyle()),
                            ),
                            InputField(
                              hintText: 'Email',
                              inputType: TextInputType.emailAddress,
                              onChanged: (val) => setState(() => email = val),
                              validator: (val) => val == null || val.isEmpty ? 'Enter email' : null,
                            ),
                          ],
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Padding(
                              padding: const EdgeInsets.only(bottom: 6),
                              child: Text('Password', style: subTitleTextStyle()),
                            ),
                            InputField(
                              hintText: 'Password',
                              isPassword: true,
                              onChanged: (val) => setState(() => password = val),
                              validator: (val) => val == null || val.isEmpty ? 'Enter password' : null,
                            ),
                          ],
                        ),
                      ),
                      SizedBox(height: 12),
                      if (isLoading) Center(child: CircularProgressIndicator()),
                      if (error.isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: Text(error, style: TextStyle(color: Colors.red)),
                        ),
                      CustomBtn(
                        text: 'Login',
                        onPressed: isLoading ? null : _login,
                      ),
                      SizedBox(height: 12),
                      CustomBtn(
                        color: secondaryColor,
                        text: 'Register',
                        onPressed: () => Navigator.pushReplacementNamed(context, '/register'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
