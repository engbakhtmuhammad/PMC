import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:csv/csv.dart';
import '../models/bef_form_model.dart';

class CsvService {
  static Future<String> exportFormsToCsv(List<BEFFormModel> forms) async {
    List<List<dynamic>> rows = [];
    rows.add(forms.isNotEmpty ? forms.first.toMap().keys.toList() : []);
    for (var form in forms) {
      rows.add(form.toMap().values.toList());
    }
    String csv = const ListToCsvConverter().convert(rows);
    final directory = await getApplicationDocumentsDirectory();
    final path = '${directory.path}/bef_forms.csv';
    final file = File(path);
    await file.writeAsString(csv);
    return path;
  }
}
