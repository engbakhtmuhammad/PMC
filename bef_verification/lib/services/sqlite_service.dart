import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'dart:convert';
import '../models/bef_form_model.dart';

class SqliteService {
  static Database? _db;

  static Future<Database> getDb() async {
    if (_db != null) return _db!;
    final path = join(await getDatabasesPath(), 'bef_forms.db');
    _db = await openDatabase(
      path,
      onCreate: (db, version) async {
        await db.execute(
          'CREATE TABLE forms(id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, created_at INTEGER, is_uploaded INTEGER DEFAULT 0, uploaded_at TEXT)'
        );
      },
      onOpen: (db) async {
        // Ensure all columns exist on existing databases
        try {
          final info = await db.rawQuery("PRAGMA table_info('forms')");
          final columnNames = info.map((row) => row['name'] as String).toList();
          
          if (!columnNames.contains('created_at')) {
            await db.execute('ALTER TABLE forms ADD COLUMN created_at INTEGER');
          }
          if (!columnNames.contains('is_uploaded')) {
            await db.execute('ALTER TABLE forms ADD COLUMN is_uploaded INTEGER DEFAULT 0');
          }
          if (!columnNames.contains('uploaded_at')) {
            await db.execute('ALTER TABLE forms ADD COLUMN uploaded_at TEXT');
          }
        } catch (_) {
          // If table doesn't exist yet or other error, ignore — onCreate will handle it.
        }
      },
      version: 2, // Increment version for schema changes
    );
    return _db!;
  }

  /// Public helper to ensure migration has been applied.
  /// Can be called from UI code to force a schema check on demand.
  static Future<void> ensureCreatedAtColumn() async {
    final db = await getDb();
    try {
      final info = await db.rawQuery("PRAGMA table_info('forms')");
      final hasCreatedAt = info.any((row) => row['name'] == 'created_at');
      if (!hasCreatedAt) {
        await db.execute('ALTER TABLE forms ADD COLUMN created_at INTEGER');
      }
    } catch (_) {
      // ignore
    }
  }

  static Future<int> saveForm(BEFFormModel form) async {
    final db = await getDb();
    final String json = jsonEncode(form.toMap());
    final now = DateTime.now().millisecondsSinceEpoch;
    return await db.insert('forms', {
      'data': json, 
      'created_at': now,
      'is_uploaded': form.isUploaded ? 1 : 0,
      'uploaded_at': form.uploadedAt,
    });
  }

  /// Update the upload status of a form
  static Future<void> markFormAsUploaded(String befCode) async {
    final db = await getDb();
    final now = DateTime.now().toIso8601String();
    
    // Find the form by befCode and update its status
    final forms = await db.query('forms');
    for (final row in forms) {
      final data = row['data']?.toString() ?? '{}';
      try {
        final Map<String, dynamic> map = jsonDecode(data) as Map<String, dynamic>;
        if (map['befCode'] == befCode) {
          // Update the JSON data to include upload status
          map['isUploaded'] = 1;
          map['uploadedAt'] = now;
          
          await db.update('forms', {
            'data': jsonEncode(map),
            'is_uploaded': 1,
            'uploaded_at': now,
          }, where: 'id = ?', whereArgs: [row['id']]);
          break;
        }
      } catch (_) {
        continue;
      }
    }
  }

  /// Update multiple forms as uploaded
  static Future<void> markFormsAsUploaded(List<String> befCodes) async {
    final db = await getDb();
    final now = DateTime.now().toIso8601String();
    
    for (final befCode in befCodes) {
      final forms = await db.query('forms');
      for (final row in forms) {
        final data = row['data']?.toString() ?? '{}';
        try {
          final Map<String, dynamic> map = jsonDecode(data) as Map<String, dynamic>;
          if (map['befCode'] == befCode) {
            // Update the JSON data to include upload status
            map['isUploaded'] = 1;
            map['uploadedAt'] = now;
            
            await db.update('forms', {
              'data': jsonEncode(map),
              'is_uploaded': 1,
              'uploaded_at': now,
            }, where: 'id = ?', whereArgs: [row['id']]);
            break;
          }
        } catch (_) {
          continue;
        }
      }
    }
  }

  static Future<List<Map<String, dynamic>>> getForms() async {
    final db = await getDb();
    return await db.query('forms', orderBy: 'created_at DESC');
  }

  static Future<List<BEFFormModel>> getFormModels() async {
    final rows = await getForms();
    return rows.map((row) {
      final data = row['data']?.toString() ?? '{}';
      try {
        final Map<String, dynamic> map = jsonDecode(data) as Map<String, dynamic>;
        return BEFFormModel.fromMap(map);
      } catch (_) {
        return BEFFormModel.fromJson(data);
      }
    }).toList();
  }

  static Future<List<Map<String, dynamic>>> getFormsRaw() async => getForms();
}
