import 'package:flutter/material.dart';
import '../services/sqlite_service.dart';
import 'view_saved_form_screen.dart';
import '../services/csv_service.dart';
import '../services/google_sheets_service.dart';
import '../widgets/custom_btn.dart';
import '../utils/constants.dart';
import '../utils/style.dart';
import '../models/bef_form_model.dart';

class SavedFormsScreen extends StatefulWidget {
  const SavedFormsScreen({Key? key}) : super(key: key);

  @override
  State<SavedFormsScreen> createState() => _SavedFormsScreenState();
}

class _SavedFormsScreenState extends State<SavedFormsScreen> {
  List<Map<String, dynamic>> _rows = [];
  List<BEFFormModel> _models = [];
  bool _loading = true;
  bool _actionLoading = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    if (!mounted) return;
    setState(() => _loading = true);
    try {
      // Ensure DB schema is up-to-date (adds columns if missing)
      await SqliteService.ensureCreatedAtColumn();
      final rows = await SqliteService.getFormsRaw();
      final models = await SqliteService.getFormModels();
      if (!mounted) return;
      setState(() {
        _rows = rows;
        _models = models;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _loading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading forms: $e'), backgroundColor: Colors.red),
      );
    }
  }

  Future<void> _exportAll() async {
    if (_rows.isEmpty) return;
    setState(() => _actionLoading = true);
    try {
      final models = await SqliteService.getFormModels();
      await CsvService.exportFormsToCsv(models);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(Icons.check_circle, color: Colors.white),
              SizedBox(width: 8),
              Expanded(child: Text('✅ Exported ${models.length} forms to CSV')),
            ],
          ),
          backgroundColor: Colors.green,
          duration: Duration(seconds: 3),
        )
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(Icons.error, color: Colors.white),
              SizedBox(width: 8),
              Expanded(child: Text('❌ Export failed: $e')),
            ],
          ),
          backgroundColor: Colors.red,
          duration: Duration(seconds: 4),
        )
      );
    }
    if (mounted) setState(() => _actionLoading = false);
  }

  Future<void> _uploadAll() async {
    if (_rows.isEmpty) return;
    setState(() => _actionLoading = true);
    try {
      final models = await SqliteService.getFormModels();
      
      // Filter out already uploaded forms
      final unuploadedModels = models.where((model) => !model.isUploaded).toList();
      
      if (unuploadedModels.isEmpty) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                Icon(Icons.info, color: Colors.white),
                SizedBox(width: 8),
                Expanded(child: Text('ℹ️ All forms have already been uploaded to Google Sheets')),
              ],
            ),
            backgroundColor: Colors.orange,
            duration: Duration(seconds: 3),
          )
        );
        setState(() => _actionLoading = false);
        return;
      }
      
      // Upload only unuploaded forms
      await GoogleSheetsService.uploadForms(unuploadedModels);
      
      // Reload the data to show updated status
      await _load();
      
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(Icons.cloud_done, color: Colors.white),
              SizedBox(width: 8),
              Expanded(child: Text('☁️ Uploaded ${unuploadedModels.length} new forms to Google Sheets')),
            ],
          ),
          backgroundColor: Colors.green,
          duration: Duration(seconds: 3),
        )
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(Icons.error, color: Colors.white),
              SizedBox(width: 8),
              Expanded(child: Text('❌ Upload failed: $e')),
            ],
          ),
          backgroundColor: Colors.red,
          duration: Duration(seconds: 4),
        )
      );
    }
    if (mounted) setState(() => _actionLoading = false);
  }

  Future<void> _exportSingle(int index) async {
    setState(() => _actionLoading = true);
    try {
      final models = await SqliteService.getFormModels();
      final model = models[index];
      await CsvService.exportFormsToCsv([model]);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('✅ Form exported to CSV'), backgroundColor: Colors.green),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('❌ Export failed: $e'), backgroundColor: Colors.red),
      );
    }
    if (mounted) setState(() => _actionLoading = false);
  }

  Future<void> _uploadSingle(int index) async {
    setState(() => _actionLoading = true);
    try {
      final models = await SqliteService.getFormModels();
      final model = models[index];
      
      if (model.isUploaded) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('ℹ️ This form has already been uploaded to Google Sheets'),
            backgroundColor: Colors.orange,
          ),
        );
        setState(() => _actionLoading = false);
        return;
      }
      
      await GoogleSheetsService.uploadForm(model);
      
      // Reload data to show updated status
      await _load();
      
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('☁️ Form uploaded to Google Sheets successfully'), backgroundColor: Colors.green),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('❌ Upload failed: $e'), backgroundColor: Colors.red),
      );
    }
    if (mounted) setState(() => _actionLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundColor,
      appBar: AppBar(
        title: Text('Visited Schools', style: titleTextStyle(color: whiteColor)),
        backgroundColor: primaryColor,
        elevation: 4,
        shadowColor: Colors.black26,
        actions: [
          IconButton(
            icon: Icon(Icons.refresh, color: whiteColor),
            onPressed: _loading ? null : _load,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _loading
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(color: primaryColor),
                  SizedBox(height: 16),
                  Text('Loading visited schools...', style: subTitleTextStyle()),
                ],
              ),
            )
          : Column(
              children: [
                // Government Header Card
                Container(
                  width: double.infinity,
                  margin: EdgeInsets.all(16),
                  padding: EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [primaryColor, primaryColor.withOpacity(0.8)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(containerRoundCorner),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black12,
                        blurRadius: 8,
                        offset: Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.business, color: whiteColor, size: 24),
                          SizedBox(width: 8),
                          Text('BEF School Verification Records', 
                               style: titleTextStyle(color: whiteColor, size: 18, fontWeight: FontWeight.bold)),
                        ],
                      ),
                      SizedBox(height: 8),
                      Text('Total Visited Schools: ${_rows.length}', 
                           style: subTitleTextStyle().copyWith(color: whiteColor.withOpacity(0.9))),
                      SizedBox(height: 4),
                      Text('Government of Pakistan - Education Foundation', 
                           style: subTitleTextStyle().copyWith(color: whiteColor.withOpacity(0.8), fontSize: 12.0)),
                    ],
                  ),
                ),

                // Action Buttons Card
                if (_rows.isNotEmpty) ...[
                  Card(
                    margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    elevation: 4,
                    shadowColor: Colors.black12,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(containerRoundCorner)),
                    child: Padding(
                      padding: EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.cloud_sync, color: primaryColor),
                              SizedBox(width: 8),
                              Text('Bulk Operations', style: titleTextStyle(color: primaryColor, fontWeight: FontWeight.bold)),
                            ],
                          ),
                          SizedBox(height: 12),
                          
                          if (_actionLoading) ...[
                            Center(
                              child: Column(
                                children: [
                                  CircularProgressIndicator(color: primaryColor),
                                  SizedBox(height: 8),
                                  Text('Processing...', style: subTitleTextStyle()),
                                ],
                              ),
                            ),
                          ] else ...[
                            Row(
                              children: [
                                Expanded(
                                  child: CustomBtn(
                                    color: const Color(0xFF2E7D32),
                                    text: 'Export All CSV',
                                    icon: Icons.file_download,
                                    onPressed: _exportAll,
                                  ),
                                ),
                                SizedBox(width: 12),
                                Expanded(
                                  child: Builder(
                                    builder: (context) {
                                      final pendingCount = _models.where((model) => !model.isUploaded).length;
                                      final totalCount = _models.length;
                                      return CustomBtn(
                                        color: pendingCount > 0 ? const Color(0xFF1976D2) : Colors.grey,
                                        text: pendingCount > 0 
                                          ? 'Upload $pendingCount Pending'
                                          : 'All $totalCount Uploaded ✓',
                                        icon: pendingCount > 0 ? Icons.cloud_upload : Icons.cloud_done,
                                        onPressed: pendingCount > 0 ? _uploadAll : null,
                                      );
                                    },
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                ],
                
                // Forms List
                Expanded(
                  child: _rows.isEmpty 
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.school_outlined, size: 80, color: Colors.grey.shade300),
                            SizedBox(height: 24),
                            Text('No School Visits Recorded', style: titleTextStyle(color: Colors.grey.shade600, size: 20)),
                            SizedBox(height: 8),
                            Text('Complete and save a BEF verification form\nto see visited schools here', 
                                 style: subTitleTextStyle().copyWith(color: Colors.grey.shade500),
                                 textAlign: TextAlign.center),
                            SizedBox(height: 24),
                            ElevatedButton.icon(
                              onPressed: () => Navigator.pop(context),
                              icon: Icon(Icons.add_location),
                              label: Text('Visit New School'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: primaryColor,
                                foregroundColor: Colors.white,
                                padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                              ),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        itemCount: _rows.length,
                        itemBuilder: (context, i) {
                          final row = _rows[i];
                          final model = i < _models.length ? _models[i] : null;
                          final createdAt = row['created_at'] as int?;
                          final date = createdAt != null ? DateTime.fromMillisecondsSinceEpoch(createdAt) : null;
                          final isUploaded = model?.isUploaded ?? false;
                          
                          return Card(
                            margin: EdgeInsets.only(bottom: 12),
                            elevation: 3,
                            shadowColor: Colors.black12,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            child: InkWell(
                              borderRadius: BorderRadius.circular(12),
                              onTap: () async {
                                final models = await SqliteService.getFormModels();
                                if (!mounted || i >= models.length) return;
                                Navigator.push(
                                  context, 
                                  MaterialPageRoute(
                                    builder: (_) => ViewSavedFormScreen(model: models[i]),
                                  ),
                                );
                              },
                              child: Padding(
                                padding: EdgeInsets.all(16),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      children: [
                                        Container(
                                          padding: EdgeInsets.all(8),
                                          decoration: BoxDecoration(
                                            color: primaryColor,
                                            borderRadius: BorderRadius.circular(8),
                                          ),
                                          child: Icon(Icons.school, color: Colors.white, size: 20),
                                        ),
                                        SizedBox(width: 12),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Row(
                                                children: [
                                                  Expanded(
                                                    child: Text('School Visit #${row['id']}', 
                                                         style: titleTextStyle(size: 16, fontWeight: FontWeight.bold)),
                                                  ),
                                                  // Upload Status Badge
                                                  Container(
                                                    padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                                    decoration: BoxDecoration(
                                                      color: isUploaded ? Colors.green : Colors.orange,
                                                      borderRadius: BorderRadius.circular(12),
                                                    ),
                                                    child: Row(
                                                      mainAxisSize: MainAxisSize.min,
                                                      children: [
                                                        Icon(
                                                          isUploaded ? Icons.cloud_done : Icons.cloud_upload,
                                                          color: Colors.white,
                                                          size: 14,
                                                        ),
                                                        SizedBox(width: 4),
                                                        Text(
                                                          isUploaded ? 'Uploaded' : 'Pending',
                                                          style: TextStyle(
                                                            color: Colors.white,
                                                            fontSize: 11.0,
                                                            fontWeight: FontWeight.bold,
                                                          ),
                                                        ),
                                                      ],
                                                    ),
                                                  ),
                                                ],
                                              ),
                                              SizedBox(height: 2),
                                              if (date != null)
                                                Text('Recorded: ${_formatDate(date)}', 
                                                     style: subTitleTextStyle().copyWith(color: Colors.grey.shade600)),
                                              if (isUploaded && model?.uploadedAt != null)
                                                Text('Uploaded: ${_formatUploadDate(model!.uploadedAt!)}', 
                                                     style: subTitleTextStyle().copyWith(color: Colors.green.shade600, fontSize: 12.0)),
                                            ],
                                          ),
                                        ),
                                        PopupMenuButton<String>(
                                          icon: Icon(Icons.more_vert, color: Colors.grey.shade600),
                                          onSelected: (value) async {
                                            if (value == 'view') {
                                              final models = await SqliteService.getFormModels();
                                              if (!mounted || i >= models.length) return;
                                              Navigator.push(
                                                context, 
                                                MaterialPageRoute(
                                                  builder: (_) => ViewSavedFormScreen(model: models[i]),
                                                ),
                                              );
                                            } else if (value == 'export') {
                                              await _exportSingle(i);
                                            } else if (value == 'upload') {
                                              await _uploadSingle(i);
                                            }
                                          },
                                          itemBuilder: (context) => [
                                            PopupMenuItem(
                                              value: 'view',
                                              child: Row(
                                                children: [
                                                  Icon(Icons.visibility, color: Colors.blue),
                                                  SizedBox(width: 8),
                                                  Text('View Details'),
                                                ],
                                              ),
                                            ),
                                            PopupMenuItem(
                                              value: 'export',
                                              child: Row(
                                                children: [
                                                  Icon(Icons.file_download, color: Colors.green),
                                                  SizedBox(width: 8),
                                                  Text('Export CSV'),
                                                ],
                                              ),
                                            ),
                                            PopupMenuItem(
                                              value: 'upload',
                                              enabled: !isUploaded, // Disable if already uploaded
                                              child: Row(
                                                children: [
                                                  Icon(
                                                    isUploaded ? Icons.cloud_done : Icons.cloud_upload, 
                                                    color: isUploaded ? Colors.grey : Colors.orange,
                                                  ),
                                                  SizedBox(width: 8),
                                                  Text(
                                                    isUploaded ? 'Already Uploaded' : 'Upload to Sheets',
                                                    style: TextStyle(
                                                      color: isUploaded ? Colors.grey : null,
                                                    ),
                                                  ),
                                                ],
                                              ),
                                            ),
                                          ],
                                        ),
                                      ],
                                    ),
                                    SizedBox(height: 12),
                                    Container(
                                      padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                      decoration: BoxDecoration(
                                        color: Colors.grey.shade50,
                                        borderRadius: BorderRadius.circular(8),
                                        border: Border.all(color: Colors.grey.shade200),
                                      ),
                                      child: Row(
                                        children: [
                                          Icon(Icons.touch_app, size: 16, color: primaryColor),
                                          SizedBox(width: 6),
                                          Text('Tap to view verification details', 
                                               style: subTitleTextStyle().copyWith(color: primaryColor, fontSize: 12.0)),
                                          Spacer(),
                                          Icon(Icons.arrow_forward_ios, size: 12, color: Colors.grey.shade400),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          );
                        },
                      ),
                ),
              ],
            ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}/${date.year} ${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
  }

  String _formatUploadDate(String isoString) {
    try {
      final dateTime = DateTime.parse(isoString);
      return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour}:${dateTime.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return isoString;
    }
  }
}
