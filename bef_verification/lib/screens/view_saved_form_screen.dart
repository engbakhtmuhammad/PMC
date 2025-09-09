import 'package:flutter/material.dart';
import '../models/bef_form_model.dart';
import '../utils/constants.dart';
import '../utils/style.dart';
import '../services/csv_service.dart';
import '../services/google_sheets_service.dart';

class ViewSavedFormScreen extends StatefulWidget {
  final BEFFormModel model;
  const ViewSavedFormScreen({Key? key, required this.model}) : super(key: key);

  @override
  State<ViewSavedFormScreen> createState() => _ViewSavedFormScreenState();
}

class _ViewSavedFormScreenState extends State<ViewSavedFormScreen> {
  bool _loading = false;

  Future<void> _exportThis() async {
    setState(() => _loading = true);
    try {
      await CsvService.exportFormsToCsv([widget.model]);
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
    if (mounted) setState(() => _loading = false);
  }

  Future<void> _uploadThis() async {
    setState(() => _loading = true);
    try {
      await GoogleSheetsService.appendRowFromModel(widget.model);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('☁️ Form uploaded to Google Sheets'), backgroundColor: Colors.green),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('❌ Upload failed: $e'), backgroundColor: Colors.red),
      );
    }
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    final schoolName = widget.model.proposedSchoolName.isNotEmpty 
        ? widget.model.proposedSchoolName 
        : widget.model.proposedSite.isNotEmpty 
            ? widget.model.proposedSite
            : 'BEF Verification Record';

    return Scaffold(
      backgroundColor: backgroundColor,
      appBar: AppBar(
        title: Text('School Verification Details', style: titleTextStyle(color: whiteColor)),
        backgroundColor: primaryColor,
        elevation: 4,
        actions: [
          PopupMenuButton<String>(
            icon: Icon(Icons.more_vert, color: whiteColor),
            onSelected: (value) {
              if (value == 'export') _exportThis();
              else if (value == 'upload') _uploadThis();
            },
            itemBuilder: (context) => [
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
                child: Row(
                  children: [
                    Icon(Icons.cloud_upload, color: Colors.blue),
                    SizedBox(width: 8),
                    Text('Upload to Sheets'),
                  ],
                ),
              ),
            ],
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
                Text('Processing...', style: subTitleTextStyle()),
              ],
            ),
          )
        : SingleChildScrollView(
            padding: EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header Card
                Card(
                  elevation: 4,
                  shadowColor: Colors.black12,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(containerRoundCorner)),
                  child: Container(
                    width: double.infinity,
                    padding: EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [primaryColor, primaryColor.withOpacity(0.8)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(containerRoundCorner),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.school, color: whiteColor, size: 28),
                            SizedBox(width: 12),
                            Expanded(
                              child: Text(schoolName, 
                                       style: titleTextStyle(color: whiteColor, size: 20, fontWeight: FontWeight.bold)),
                            ),
                          ],
                        ),
                        SizedBox(height: 8),
                        if (widget.model.befCode.isNotEmpty)
                          Text('BEF Code: ${widget.model.befCode}', 
                               style: subTitleTextStyle().copyWith(color: whiteColor.withOpacity(0.9))),
                        if (widget.model.district.isNotEmpty)
                          Text('District: ${widget.model.district}', 
                               style: subTitleTextStyle().copyWith(color: whiteColor.withOpacity(0.9))),
                      ],
                    ),
                  ),
                ),

                SizedBox(height: 16),

                // Basic Information
                _buildSection(
                  'Basic Site Information',
                  Icons.location_on,
                  [
                    _buildInfoRow('Date of Visit', widget.model.dateOfVisit),
                    _buildInfoRow('Proposed Site/Village', widget.model.proposedSite),
                    _buildInfoRow('Proposed School Name', widget.model.proposedSchoolName),
                    _buildInfoRow('District', widget.model.district),
                    _buildInfoRow('Tehsil', widget.model.tehsil),
                    _buildInfoRow('Union Council', widget.model.unionCouncil),
                    _buildInfoRow('Village Name', widget.model.villageName),
                    _buildInfoRow('Distance from District HQ', widget.model.distanceFromHQ + (widget.model.distanceFromHQ.isNotEmpty ? ' KM' : '')),
                    _buildInfoRow('Total Households', widget.model.totalHouseholds),
                    _buildInfoRow('Functional Status', widget.model.functionalStatus),
                    if (widget.model.nonFunctionalReason.isNotEmpty)
                      _buildInfoRow('Non-Functional Reason', widget.model.nonFunctionalReason),
                  ],
                ),

                // GPS Coordinates
                _buildSection(
                  'GPS Coordinates & Nearby School',
                  Icons.gps_fixed,
                  [
                    if (widget.model.gpsNearestSchoolX.isNotEmpty || widget.model.gpsNearestSchoolY.isNotEmpty)
                      _buildInfoRow('Nearest School GPS', 
                          '${widget.model.gpsNearestSchoolX}, ${widget.model.gpsNearestSchoolY}'),
                    if (widget.model.gpsProposedSiteX.isNotEmpty || widget.model.gpsProposedSiteY.isNotEmpty)
                      _buildInfoRow('Proposed Site GPS', 
                          '${widget.model.gpsProposedSiteX}, ${widget.model.gpsProposedSiteY}'),
                    _buildInfoRow('Nearest School BEMIS Code', widget.model.nearestSchoolBEMISCode),
                    _buildInfoRow('Nearest Govt School Name', widget.model.nearestGovtSchoolName),
                    _buildInfoRow('Nearest School Gender', widget.model.nearestGovtSchoolGender),
                    _buildInfoRow('Nearest School Level', widget.model.nearestGovtSchoolLevel),
                    _buildInfoRow('Distance from Proposed Site', 
                        widget.model.distanceFromProposedSite + (widget.model.distanceFromProposedSite.isNotEmpty ? ' KM' : '')),
                  ],
                ),

                // OOSC Information
                _buildSection(
                  'Out-of-School Children (Ages 5-10)',
                  Icons.child_care,
                  [
                    _buildInfoRow('OOSC Boys', widget.model.ooscBoys),
                    _buildInfoRow('OOSC Girls', widget.model.ooscGirls),
                    _buildInfoRow('OOSC Total', widget.model.ooscTotal),
                  ],
                ),

                // Qualified Persons
                _buildSection(
                  'Qualified Persons Available for Teaching',
                  Icons.school_outlined,
                  [
                    _buildInfoRow('Matric', widget.model.qualifiedMatric),
                    _buildInfoRow('FA/FSc', widget.model.qualifiedFAFSc),
                    _buildInfoRow('BA/BSc', widget.model.qualifiedBABSc),
                    _buildInfoRow('MA/MSc', widget.model.qualifiedMAMSc),
                  ],
                ),

                // Primary Teacher Info
                if (widget.model.teacherName.isNotEmpty || widget.model.teacherCNIC.isNotEmpty) 
                  _buildSection(
                    'Primary Teacher Information',
                    Icons.person,
                    [
                      _buildInfoRow('Teacher Name', widget.model.teacherName),
                      _buildInfoRow('Teacher CNIC', widget.model.teacherCNIC),
                      _buildInfoRow('Teacher Contact', widget.model.teacherContact),
                      _buildInfoRow('Teacher Qualification', widget.model.teacherQualification),
                    ],
                  ),

                // Selected Teachers List
                if (widget.model.teachers.isNotEmpty)
                  _buildSection(
                    'Selected/Qualified Teachers',
                    Icons.group,
                    [
                      Container(
                        decoration: BoxDecoration(
                          color: Colors.grey.shade50,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.grey.shade200),
                        ),
                        child: Column(
                          children: widget.model.teachers.asMap().entries.map((entry) {
                            final index = entry.key;
                            final teacher = entry.value;
                            return Container(
                              padding: EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                border: index > 0 ? Border(top: BorderSide(color: Colors.grey.shade200)) : null,
                              ),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Container(
                                    padding: EdgeInsets.all(6),
                                    decoration: BoxDecoration(
                                      color: primaryColor,
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: Text('${index + 1}', 
                                             style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12.0)),
                                  ),
                                  SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(teacher['name'] ?? 'N/A', 
                                             style: titleTextStyle(size: 14, fontWeight: FontWeight.bold)),
                                        if ((teacher['cnic'] ?? '').isNotEmpty)
                                          Text('CNIC: ${teacher['cnic']}', style: subTitleTextStyle()),
                                        if ((teacher['contact'] ?? '').isNotEmpty)
                                          Text('Contact: ${teacher['contact']}', style: subTitleTextStyle()),
                                        if ((teacher['qualification'] ?? '').isNotEmpty)
                                          Text('Qualification: ${teacher['qualification']}', style: subTitleTextStyle()),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            );
                          }).toList(),
                        ),
                      ),
                    ],
                  ),

                // Infrastructure
                _buildSection(
                  'Infrastructure & Facilities',
                  Icons.business,
                  [
                    _buildInfoRow('Building Structure', widget.model.buildingStructure),
                    _buildInfoRow('Existing/Allocated Rooms', widget.model.allocatedRooms),
                    _buildInfoRow('Toilets', widget.model.toilets),
                    _buildInfoRow('Space for New Rooms', widget.model.spaceForNewRooms),
                    _buildInfoRow('Boundary Wall', widget.model.boundaryWall),
                    _buildInfoRow('Boundary Wall Status', widget.model.boundaryWallStatus),
                    _buildInfoRow('Furniture - Chairs', widget.model.furnitureChairs),
                    _buildInfoRow('Furniture - Table', widget.model.furnitureTable),
                    _buildInfoRow('Furniture - Tat', widget.model.furnitureTat),
                  ],
                ),

                // Current Enrollment
                if (widget.model.currentEnrollmentTotal.isNotEmpty || 
                    widget.model.currentEnrollmentBoys.isNotEmpty || 
                    widget.model.currentEnrollmentGirls.isNotEmpty)
                  _buildSection(
                    'Current BEF Enrollment',
                    Icons.groups,
                    [
                      _buildInfoRow('Girls', widget.model.currentEnrollmentGirls),
                      _buildInfoRow('Boys', widget.model.currentEnrollmentBoys),
                      _buildInfoRow('Total', widget.model.currentEnrollmentTotal),
                    ],
                  ),

                // Remarks
                if (widget.model.remarks.isNotEmpty)
                  _buildSection(
                    'Remarks & Observations',
                    Icons.note_alt,
                    [
                      Container(
                        width: double.infinity,
                        padding: EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.grey.shade50,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.grey.shade200),
                        ),
                        child: Text(widget.model.remarks, 
                                 style: subTitleTextStyle().copyWith(height: 1.4)),
                      ),
                    ],
                  ),

                // Verified By
                _buildSection(
                  'Verification Information',
                  Icons.verified,
                  [
                    _buildInfoRow('Verified By', widget.model.verifiedByName),
                    _buildInfoRow('Designation', widget.model.verifiedByDesignation),
                    _buildInfoRow('District', widget.model.verifiedByDistrict),
                    _buildInfoRow('Contact Number', widget.model.verifiedByContact),
                    _buildInfoRow('Verification Date', widget.model.verifiedByDate),
                  ],
                ),

                SizedBox(height: 24),

                // Action Buttons at bottom
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: _exportThis,
                        icon: Icon(Icons.file_download),
                        label: Text('Export CSV'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          foregroundColor: Colors.white,
                          padding: EdgeInsets.symmetric(vertical: 12),
                        ),
                      ),
                    ),
                    SizedBox(width: 12),
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: _uploadThis,
                        icon: Icon(Icons.cloud_upload),
                        label: Text('Upload to Sheets'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blue,
                          foregroundColor: Colors.white,
                          padding: EdgeInsets.symmetric(vertical: 12),
                        ),
                      ),
                    ),
                  ],
                ),

                SizedBox(height: 16),
              ],
            ),
          ),
    );
  }

  Widget _buildSection(String title, IconData icon, List<Widget> children) {
    return Card(
      margin: EdgeInsets.only(bottom: 16),
      elevation: 2,
      shadowColor: Colors.black12,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(containerRoundCorner)),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: primaryColor, size: 22),
                SizedBox(width: 8),
                Text(title, style: titleTextStyle(color: primaryColor, size: 16, fontWeight: FontWeight.bold)),
              ],
            ),
            SizedBox(height: 12),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    if (value.isEmpty) return SizedBox.shrink();
    
    return Padding(
      padding: EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(label + ':', 
                     style: subTitleTextStyle().copyWith(fontWeight: FontWeight.w500)),
          ),
          Expanded(
            child: Text(value, 
                     style: subTitleTextStyle().copyWith(color: Colors.black87)),
          ),
        ],
      ),
    );
  }
}
