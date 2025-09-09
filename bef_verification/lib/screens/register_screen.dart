import 'package:flutter/material.dart';
import '../models/user_model.dart';
import '../services/auth_service.dart';
import '../utils/constants.dart';
import '../utils/style.dart';
import '../widgets/input_field.dart';
import '../widgets/custom_btn.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({Key? key}) : super(key: key);

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final AuthService _authService = AuthService();

  String firstName = '';
  String lastName = '';
  String phoneNumber = '';
  String email = '';
  String cnic = '';
  String district = '';
  String gender = '';
  String designation = '';
  String password = '';

  bool isLoading = false;
  String error = '';

  void _register() async {
    if (_formKey.currentState!.validate()) {
      setState(() { isLoading = true; error = ''; });
      UserModel user = UserModel(
        firstName: firstName,
        lastName: lastName,
        phoneNumber: phoneNumber,
        email: email,
        cnic: cnic,
        district: district,
        gender: gender,
        designation: designation,
      );
      try {
        await _authService.registerWithEmailAndPassword(user, password);
        setState(() { isLoading = false; });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Registration successful!')),
        );
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
        title: Text('User Registration', style: titleTextStyle(color: whiteColor)),
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
                      Text('Create Account', style: titleTextStyle(size: 24, color: primaryColor, fontWeight: FontWeight.bold), textAlign: TextAlign.center),
                      SizedBox(height: 24),
                      _labeled('First Name', InputField(
                        hintText: 'First Name',
                        onChanged: (val) => setState(() => firstName = val),
                        validator: (val) => val == null || val.isEmpty ? 'Enter first name' : null,
                      )),
                      _labeled('Last Name', InputField(
                        hintText: 'Last Name',
                        onChanged: (val) => setState(() => lastName = val),
                        validator: (val) => val == null || val.isEmpty ? 'Enter last name' : null,
                      )),
                      _labeled('Phone Number', InputField(
                        hintText: 'Phone Number',
                        inputType: TextInputType.phone,
                        onChanged: (val) => setState(() => phoneNumber = val),
                        validator: (val) => val == null || val.isEmpty ? 'Enter phone number' : null,
                      )),
                      _labeled('Email', InputField(
                        hintText: 'Email',
                        inputType: TextInputType.emailAddress,
                        onChanged: (val) => setState(() => email = val),
                        validator: (val) => val == null || val.isEmpty ? 'Enter email' : null,
                      )),
                      _labeled('CNIC', InputField(
                        hintText: 'CNIC',
                        onChanged: (val) => setState(() => cnic = val),
                        validator: (val) => val == null || val.isEmpty ? 'Enter CNIC' : null,
                      )),
                      _labeled('District', InputField(
                        hintText: 'District',
                        onChanged: (val) => setState(() => district = val),
                        validator: (val) => val == null || val.isEmpty ? 'Enter district' : null,
                      )),
                      _labeled('Gender', Container(
                        decoration: BoxDecoration(color: greyColor, borderRadius: BorderRadius.circular(containerRoundCorner)),
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        child: DropdownButtonFormField<String>(
                          decoration: const InputDecoration(border: InputBorder.none),
                          items: ['Male', 'Female'].map((g) => DropdownMenuItem(value: g, child: Text(g))).toList(),
                          onChanged: (val) => setState(() => gender = val ?? ''),
                          validator: (val) => val == null || val.isEmpty ? 'Select gender' : null,
                        ),
                      )),
                      _labeled('Designation', InputField(
                        hintText: 'Designation',
                        onChanged: (val) => setState(() => designation = val),
                        validator: (val) => val == null || val.isEmpty ? 'Enter designation' : null,
                      )),
                      _labeled('Password', InputField(
                        hintText: 'Password',
                        isPassword: true,
                        onChanged: (val) => setState(() => password = val),
                        validator: (val) => val == null || val.length < 6 ? 'Enter min 6 char password' : null,
                      )),
                      SizedBox(height: 16),
                      if (isLoading) Center(child: CircularProgressIndicator()),
                      if (error.isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: Text(error, style: TextStyle(color: Colors.red)),
                        ),
                      CustomBtn(
                        text: 'Register',
                        onPressed: isLoading ? null : _register,
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

  Widget _labeled(String label, Widget child) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Text(label, style: subTitleTextStyle()),
          ),
          child,
        ],
      ),
    );
  }
}
