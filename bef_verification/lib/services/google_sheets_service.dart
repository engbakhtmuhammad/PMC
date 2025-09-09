import 'package:googleapis/sheets/v4.dart' as sheets;
import 'package:googleapis_auth/auth_io.dart' as auth;
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/bef_form_model.dart';
import 'sqlite_service.dart';

class GoogleSheetsService {
  static const _credentials = r'''
{
  "type": "service_account",
  "project_id": "befverification-1",
  "private_key_id": "30588a3f64b74a4b99d1fc34f7f421dde5ccca01",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC32rUl3RtBGNe8\nELDusxzBTNFMZmTvRlvqHAmgxdBH/MbitW03Q0RWvKF3Q/a8X1FYf/UHjvDk38ng\nWeATzQfZYMpnZxngHrMWknorhxsNsEE9LOH2yrU5etiyGBaU2tgp3SbTOhuDZCp0\n60eYUeApTFVyQwt8CH8ChLlImk5UVHUXpTqKleX7dJMXqiwpTx4CwYRoZ1EZUlH4\n3KQDQlhlLM+ISy+gF7ATyoW8DW0+8yigDW3SYEIyVCJ02QbmflVByE01GBlkVqvv\nWblA5un1+K8rooCCiXPrDB6b5UPUvNxcXMjKx+nKb6jNyhaK4RZNyiC3eK7N9d33\nUGgmdyzfAgMBAAECggEAB639ihbZyBbTEBp8YYQey947Ed9nEO2V8kn4hvwsTo16\n+0ZLyRaouJzJe9Ndb5HlsnYp1IZ+fnjwlEv8xab3UHewDLCsToXJwkQdEUtj8Gbv\n2q/Qwn/GISAGBC5oZxBbHiiMMh+Hva3F7jtTssOcwuza1tqBFM3ADGlh2ewEIJaS\naofS3NKS+UfVQdtiqSukl+W6e99OT7EzJ3HHkgxSKWR/wQlREm23NEZ9qNtEsN5k\nunmOKTLhEZv1qsGSpm2BCtL1s7VTMJVVPeHjIEFrmo35REFhssRJ3gSH0JcVltkc\nI5S8NhjEaw4bm8IPNH7R1E1YsnxZG4lw95q+cP5wzQKBgQDd6nY4LEgynpAmrfCD\nEG0bzIlZN8DVGnjD83yiMaHoGqdiaYjVmHbxoeBTCErc+oJkRnMnRtg4EsC+YLK/\nXkn6LSU3ui8L0vkPhwBrxBTt+5YRReGZikLjyGiIuFMeVcZqNQrkNUDOyi8iM1E9\nZO8UWQPhirnGzclJmZw0MNHX5QKBgQDUF7MEXYO5pFtHXOZz+ZLGo2p9zU8rhnJr\nx9kD8GdT158tGusdUKMRxMBzAjoGmVhZqRyH15pX+frLNOeJ+Z/+19n5sK313r99\n5rk/0iY1ZjOwQH82KfsJTap5ft0VLwjeqTmxEo+FQHLGfMPZ/Bg5ridFCQS1C5QZ\n8wd5g2FdcwKBgDvyooz6KWbDPt20D0zYmyDvWAsp7IWk6QrGM9z822gAC0eiirxo\nu3j66caEbvTTF3ZPMbxifvZm2nqTVLYtmn5iw7MSMLNZAr8XER4LkjvXwupXnmID\n3534/YQxhwKi2T7HpXGQkTlLlQAALOoQ4iT1Bv9eomD6Jm4jePcAWS+hAoGAJOpn\nF1hriBFqbdZmqkMDYB2reHAW2p2RJt9nD391jKtYIlKwH68cYwha8umtTd68+QYt\nWBuX2r5A/8OalXJkfcf2QbaV4Ni/fdt93PTn/51lW8UuHzBZaHojNPh25KwGIDNW\nPlLbtjbMg23N7RAq60c7wJFcR2LXiVi6sVTDyq8CgYBBwdwI8+KUNFdN+IVDqbHK\nDn0rxB6f2PNCwR85hRv7MGIMLHyM5RIcNWRjup9Af+b5wiFd3yPK1yWenDE3JuAp\nbYedXaIvyT/ZI5UNfdtngdQY04+Ni+bElahMR1x0ZGQt816xhh10+uK+uv8ZiMQh\nCya15O54oWRrSo8STj4/lw==\n-----END PRIVATE KEY-----\n",
  "client_email": "befverification@befverification-1.iam.gserviceaccount.com",
  "client_id": "107921929783164922682",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/befverification%40befverification-1.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
''';
  
  static const _scopes = [sheets.SheetsApi.spreadsheetsScope];
  static const _spreadsheetId = '1bseEOw2a_S3-AoXSSsj2UvIaHBAtz3hlpexvpXfRprU';
  static const _sheetName = 'Sheet1'; // Change if your sheet name is different

  /// Get authenticated HTTP client using service account credentials
  static Future<http.Client> _getAuthenticatedClient() async {
    try {
      final credentialsMap = jsonDecode(_credentials);
      final credentials = auth.ServiceAccountCredentials.fromJson(credentialsMap);
      
      final client = await auth.clientViaServiceAccount(credentials, _scopes);
      return client;
    } catch (e) {
      throw Exception('Failed to authenticate with Google Sheets: $e');
    }
  }

  /// Ensure headers exist in the sheet
  static Future<void> _ensureHeaders(sheets.SheetsApi sheetsApi) async {
    try {
      // Check if the sheet has any data
      final existingData = await sheetsApi.spreadsheets.values.get(
        _spreadsheetId, 
        '$_sheetName!A1:Z1', // Check first row for headers
      );
      
      // If no data or first row is empty, create headers
      if (existingData.values == null || existingData.values!.isEmpty) {
        // Create a dummy form to get the headers
        final dummyForm = BEFFormModel();
        final map = dummyForm.toMap();
        final keys = map.keys.toList()..sort(); // Sort for consistent column order
        
        // Add headers as the first row
        await sheetsApi.spreadsheets.values.update(
          sheets.ValueRange(values: [keys]),
          _spreadsheetId,
          '$_sheetName!A1:${_getColumnLetter(keys.length)}1',
          valueInputOption: 'RAW',
        );
      }
    } catch (e) {
      // If sheet doesn't exist or other error, create headers anyway
      final dummyForm = BEFFormModel();
      final map = dummyForm.toMap();
      final keys = map.keys.toList()..sort();
      
      await sheetsApi.spreadsheets.values.update(
        sheets.ValueRange(values: [keys]),
        _spreadsheetId,
        '$_sheetName!A1:${_getColumnLetter(keys.length)}1',
        valueInputOption: 'RAW',
      );
    }
  }

  /// Get column letter (A, B, C, ..., Z, AA, AB, ...)
  static String _getColumnLetter(int columnNumber) {
    String result = '';
    while (columnNumber > 0) {
      columnNumber--;
      result = String.fromCharCode(65 + (columnNumber % 26)) + result;
      columnNumber = columnNumber ~/ 26;
    }
    return result;
  }

  /// Format value for Google Sheets (handle complex types like Lists)
  static String _formatValueForGoogleSheets(dynamic value) {
    if (value == null) return '';
    if (value is List) {
      // Convert list of maps to a readable string format
      if (value.isEmpty) return '';
      try {
        final items = value.map((item) {
          if (item is Map) {
            final pairs = item.entries
                .where((e) => e.value != null && e.value.toString().isNotEmpty)
                .map((e) => '${e.key}: ${e.value}')
                .join(', ');
            return pairs.isNotEmpty ? '{$pairs}' : '';
          }
          return item.toString();
        }).where((item) => item.isNotEmpty).toList();
        return items.join(' | ');
      } catch (e) {
        return value.toString();
      }
    }
    return value.toString();
  }

  /// Upload a single form to Google Sheets
  static Future<void> uploadForm(BEFFormModel form) async {
    try {
      final client = await _getAuthenticatedClient();
      final sheetsApi = sheets.SheetsApi(client);

      // Ensure headers exist first
      await _ensureHeaders(sheetsApi);

      // Convert form to row data - ensure consistent ordering
      final map = form.toMap();
      final keys = map.keys.toList()..sort(); // Sort for consistent column order
      final values = [keys.map((k) => _formatValueForGoogleSheets(map[k])).toList()];

      // Use append method which automatically finds the next available row
      // But first we need to make sure we're appending after existing data
      await sheetsApi.spreadsheets.values.append(
        sheets.ValueRange(values: values),
        _spreadsheetId,
        '$_sheetName!A:A', // This tells it to append after existing data
        valueInputOption: 'RAW',
        insertDataOption: 'INSERT_ROWS', // This ensures it adds new rows
      );
      
      client.close();
      
      // Mark form as uploaded in local database
      if (form.befCode.isNotEmpty) {
        await SqliteService.markFormAsUploaded(form.befCode);
      }
    } catch (e) {
      throw Exception('Failed to upload form to Google Sheets: $e');
    }
  }

  /// Upload multiple forms to Google Sheets in batch
  static Future<void> uploadForms(List<BEFFormModel> forms) async {
    if (forms.isEmpty) return;
    
    try {
      final client = await _getAuthenticatedClient();
      final sheetsApi = sheets.SheetsApi(client);

      // Ensure headers exist first
      await _ensureHeaders(sheetsApi);

      // Convert all forms to rows - ensure consistent ordering
      final map = forms.first.toMap();
      final keys = map.keys.toList()..sort(); // Sort for consistent column order
      
      final values = forms.map((form) {
        final formMap = form.toMap();
        return keys.map((k) => _formatValueForGoogleSheets(formMap[k])).toList();
      }).toList();

      // Use append method for batch upload
      await sheetsApi.spreadsheets.values.append(
        sheets.ValueRange(values: values),
        _spreadsheetId,
        '$_sheetName!A:A', // This tells it to append after existing data
        valueInputOption: 'RAW',
        insertDataOption: 'INSERT_ROWS', // This ensures it adds new rows
      );
      
      client.close();
      
      // Mark all forms as uploaded in local database
      final befCodes = forms.where((f) => f.befCode.isNotEmpty).map((f) => f.befCode).toList();
      if (befCodes.isNotEmpty) {
        await SqliteService.markFormsAsUploaded(befCodes);
      }
    } catch (e) {
      throw Exception('Failed to upload forms to Google Sheets: $e');
    }
  }

  /// Create headers row in the sheet (call this once to set up the sheet)
  static Future<void> createHeaders() async {
    try {
      final client = await _getAuthenticatedClient();
      final sheetsApi = sheets.SheetsApi(client);

      await _ensureHeaders(sheetsApi);
      
      client.close();
    } catch (e) {
      throw Exception('Failed to create headers in Google Sheets: $e');
    }
  }

  /// Helper: append a flattened row from BEFFormModel (keeping for backward compatibility)
  static Future<void> appendRowFromModel(BEFFormModel form) async {
    await uploadForm(form);
  }

  /// Clear all data in the sheet and recreate headers (use with caution)
  static Future<void> clearSheetAndCreateHeaders() async {
    try {
      final client = await _getAuthenticatedClient();
      final sheetsApi = sheets.SheetsApi(client);

      // Clear all data
      await sheetsApi.spreadsheets.values.clear(
        sheets.ClearValuesRequest(),
        _spreadsheetId,
        _sheetName,
      );

      // Create headers
      await _ensureHeaders(sheetsApi);
      
      client.close();
    } catch (e) {
      throw Exception('Failed to clear sheet and create headers: $e');
    }
  }

  /// Get all data from the sheet (for debugging/verification)
  static Future<List<List<String>>> getAllData() async {
    try {
      final client = await _getAuthenticatedClient();
      final sheetsApi = sheets.SheetsApi(client);

      final data = await sheetsApi.spreadsheets.values.get(
        _spreadsheetId, 
        _sheetName,
      );
      
      client.close();

      if (data.values == null) return [];
      
      return data.values!.map((row) => 
        row.map((cell) => cell?.toString() ?? '').toList()
      ).toList();
    } catch (e) {
      throw Exception('Failed to get data from Google Sheets: $e');
    }
  }

  /// Get the count of rows with data (excluding headers)
  static Future<int> getDataRowCount() async {
    try {
      final allData = await getAllData();
      if (allData.isEmpty) return 0;
      
      // Subtract 1 for headers
      return allData.length - 1;
    } catch (e) {
      return 0;
    }
  }

  /// Get just the headers from the sheet
  static Future<List<String>> getHeaders() async {
    try {
      final client = await _getAuthenticatedClient();
      final sheetsApi = sheets.SheetsApi(client);

      final data = await sheetsApi.spreadsheets.values.get(
        _spreadsheetId, 
        '$_sheetName!1:1', // Just first row
      );
      
      client.close();

      if (data.values == null || data.values!.isEmpty) return [];
      
      return data.values!.first.map((cell) => cell?.toString() ?? '').toList();
    } catch (e) {
      return [];
    }
  }

  /// Check if the sheet has proper structure (headers exist)
  static Future<bool> hasHeaders() async {
    try {
      final client = await _getAuthenticatedClient();
      final sheetsApi = sheets.SheetsApi(client);

      final existingData = await sheetsApi.spreadsheets.values.get(
        _spreadsheetId, 
        '$_sheetName!A1:Z1',
      );
      
      client.close();
      
      return existingData.values != null && existingData.values!.isNotEmpty;
    } catch (e) {
      return false;
    }
  }

  /// Get column names in the order they are stored in Google Sheets
  static List<String> getColumnNamesInOrder() {
    final dummyForm = BEFFormModel();
    final map = dummyForm.toMap();
    final keys = map.keys.toList()..sort(); // Sort for consistent column order
    return keys;
  }

  /// Print column names in order (for debugging)
  static void printColumnOrder() {
    final columns = getColumnNamesInOrder();
    print('Google Sheets Column Order (Total: ${columns.length} columns):');
    print('');
    for (int i = 0; i < columns.length; i++) {
      print('${(i + 1).toString().padLeft(2)}. ${columns[i]}');
    }
    print('');
    print('Column names as comma-separated list:');
    print(columns.join(', '));
  }
}
