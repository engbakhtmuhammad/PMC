import 'package:flutter/material.dart';
import '../utils/constants.dart';
import '../utils/style.dart';
import '../services/sqlite_service.dart';
import '../models/bef_form_model.dart';

class VisitedSchoolsScreen extends StatefulWidget {
  const VisitedSchoolsScreen({super.key});

  @override
  State<VisitedSchoolsScreen> createState() => _VisitedSchoolsScreenState();
}

class _VisitedSchoolsScreenState extends State<VisitedSchoolsScreen> {
  late Future<List<BEFFormModel>> _formsFuture;

  @override
  void initState() {
    super.initState();
    _formsFuture = SqliteService.getFormModels();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Visited Schools', style: titleTextStyle(color: whiteColor)),
        backgroundColor: primaryColor,
        elevation: 0,
      ),
      backgroundColor: backgroundColor,
      body: FutureBuilder<List<BEFFormModel>>(
        future: _formsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          final forms = snapshot.data ?? [];
          if (forms.isEmpty) {
            return Center(child: Text('No visited schools yet', style: subTitleTextStyle()));
          }
          return ListView.separated(
            padding: EdgeInsets.all(defaultPadding),
            itemCount: forms.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final f = forms[index];
              return Card(
                elevation: 1,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(containerRoundCorner)),
                child: ListTile(
                  title: Text(f.proposedSchoolName.isNotEmpty ? f.proposedSchoolName : 'Unnamed School', style: titleTextStyle(size: 16)),
                  subtitle: Text('${f.district} • ${f.tehsil}', style: descriptionTextStyle()),
                ),
              );
            },
          );
        },
      ),
    );
  }
} 