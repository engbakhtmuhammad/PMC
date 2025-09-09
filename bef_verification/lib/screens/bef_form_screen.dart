import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../models/bef_form_model.dart';
import '../services/sqlite_service.dart';
import '../services/csv_service.dart';
import '../services/google_sheets_service.dart';
import '../utils/constants.dart';
import '../utils/style.dart';
import '../widgets/input_field.dart';
import '../widgets/custom_btn.dart';

class BEFFormScreen extends StatefulWidget {
  const BEFFormScreen({Key? key}) : super(key: key);

  @override
  State<BEFFormScreen> createState() => _BEFFormScreenState();
}

class _BEFFormScreenState extends State<BEFFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final BEFFormModel formData = BEFFormModel();
  bool isLoading = false;
  String error = '';
  bool _gettingLocation = false;
  List<Map<String, String>> _teachers = [];
  
  // Date picker controller
  final TextEditingController _dateController = TextEditingController();
  
  // Furniture selections
  Map<String, bool> furnitureSelections = {
    'Chairs': false,
    'Tables': false,
    'Tat': false,
  };
  
  // Furniture count controllers
  late Map<String, TextEditingController> furnitureCountControllers;

  @override
  void initState() {
    super.initState();
    // Set current date as default
    final now = DateTime.now();
    _dateController.text = '${now.day.toString().padLeft(2, '0')}/${now.month.toString().padLeft(2, '0')}/${now.year}';
    formData.dateOfVisit = _dateController.text;
    
    // Initialize furniture count controllers
    furnitureCountControllers = {
      'Chairs': TextEditingController(),
      'Tables': TextEditingController(),
      'Tat': TextEditingController(),
    };
  }

  @override
  void dispose() {
    _dateController.dispose();
    furnitureCountControllers.values.forEach((controller) => controller.dispose());
    super.dispose();
  }

  void _saveLocally() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { isLoading = true; error = ''; });
    try {
  formData.teachers = _teachers;
  await SqliteService.saveForm(formData);
      setState(() { isLoading = false; });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Saved locally!')),
      );
    } catch (e) {
      setState(() { error = e.toString(); isLoading = false; });
    }
  }

  void _exportToCsv() async {
    setState(() { isLoading = true; error = ''; });
    try {
      final formModels = await SqliteService.getFormModels();
      final path = await CsvService.exportFormsToCsv(formModels);
      setState(() { isLoading = false; });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Exported to CSV: $path')),
      );
    } catch (e) {
      setState(() { error = e.toString(); isLoading = false; });
    }
  }

  void _uploadToGoogleSheets() async {
    if (!_formKey.currentState!.validate()) return;
    
    // Check if already uploaded
    if (formData.isUploaded) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('This form has already been uploaded to Google Sheets!'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }
    
    setState(() { isLoading = true; error = ''; });
    try {
      formData.teachers = _teachers;
      await GoogleSheetsService.uploadForm(formData);
      
      // Update the local form status
      setState(() { 
        formData.isUploaded = true;
        formData.uploadedAt = DateTime.now().toIso8601String();
        isLoading = false; 
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Successfully uploaded to Google Sheets!'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      setState(() { error = e.toString(); isLoading = false; });
    }
  }

  Future<void> _getCurrentLocation() async {
    setState(() { _gettingLocation = true; });
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        setState(() { _gettingLocation = false; });
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Location services are disabled.')));
        return;
      }
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          setState(() { _gettingLocation = false; });
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Location permission denied')));
          return;
        }
      }
      if (permission == LocationPermission.deniedForever) {
        setState(() { _gettingLocation = false; });
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Location permission permanently denied')));
        return;
      }

      final pos = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.best);
    if (!mounted) return;
      setState(() {
        formData.gpsProposedSiteX = pos.latitude.toString();
        formData.gpsProposedSiteY = pos.longitude.toString();
        _gettingLocation = false;
      });
    if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Coordinates captured')));
    } catch (e) {
    if (!mounted) return;
      setState(() { _gettingLocation = false; });
    if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error getting location: $e')));
    }
  }

  void _addTeacher() async {
    final nameCtrl = TextEditingController();
    final cnicCtrl = TextEditingController();
    final contactCtrl = TextEditingController();
    String selectedQualification = 'BS';
    final subjectCtrl = TextEditingController();
    
    final result = await showDialog<bool>(
      context: context,
      builder: (_) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: Text('Add New Teacher', style: TextStyle(fontWeight: FontWeight.bold)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nameCtrl, 
                  decoration: InputDecoration(
                    labelText: 'Full Name*',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.person),
                  ),
                ),
                SizedBox(height: 12),
                
                // CNIC with validation (13 digits)
                TextField(
                  controller: cnicCtrl, 
                  decoration: InputDecoration(
                    labelText: 'CNIC (13 digits)*',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.credit_card),
                    hintText: '1234567890123',
                  ),
                  keyboardType: TextInputType.number,
                  maxLength: 13,
                ),
                SizedBox(height: 12),
                
                // Contact with validation (11 digits)
                TextField(
                  controller: contactCtrl, 
                  decoration: InputDecoration(
                    labelText: 'Contact Number (11 digits)',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.phone),
                    hintText: '03001234567',
                  ),
                  keyboardType: TextInputType.phone,
                  maxLength: 11,
                ),
                SizedBox(height: 12),
                
                // Qualification dropdown
                DropdownButtonFormField<String>(
                  value: selectedQualification,
                  decoration: InputDecoration(
                    labelText: 'Qualification*',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.school),
                  ),
                  items: ['BS', 'MS', 'Matric', 'FSc', 'PhD'].map((qual) => 
                    DropdownMenuItem(value: qual, child: Text(qual))
                  ).toList(),
                  onChanged: (value) {
                    setState(() {
                      selectedQualification = value!;
                    });
                  },
                ),
                SizedBox(height: 12),
                
                // Subject/Degree name
                TextField(
                  controller: subjectCtrl, 
                  decoration: InputDecoration(
                    labelText: 'Subject/Degree Name',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.subject),
                    hintText: 'e.g., Mathematics, Computer Science',
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false), 
              child: Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                // Validation
                if (nameCtrl.text.trim().isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Teacher name is required!')),
                  );
                  return;
                }
                
                if (cnicCtrl.text.trim().isNotEmpty && cnicCtrl.text.trim().length != 13) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('CNIC must be exactly 13 digits!')),
                  );
                  return;
                }
                
                if (cnicCtrl.text.trim().isNotEmpty && !RegExp(r'^\d+$').hasMatch(cnicCtrl.text.trim())) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('CNIC must contain only numbers!')),
                  );
                  return;
                }
                
                if (contactCtrl.text.trim().isNotEmpty && contactCtrl.text.trim().length != 11) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Contact number must be exactly 11 digits!')),
                  );
                  return;
                }
                
                Navigator.pop(context, true);
              },
              child: Text('Add Teacher'),
            ),
          ],
        ),
      ),
    );
    
    if (result == true) {
      setState(() {
        _teachers.add({
          'name': nameCtrl.text.trim(),
          'cnic': cnicCtrl.text.trim(),
          'contact': contactCtrl.text.trim(),
          'qualification': selectedQualification + (subjectCtrl.text.trim().isNotEmpty ? ' (${subjectCtrl.text.trim()})' : ''),
        });
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Teacher added successfully!')),
      );
    }
  }

  void _showDeleteTeacherDialog(int idx) async {
    if (idx < 0 || idx >= _teachers.length) return;
    
    final teacher = _teachers[idx];
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Remove Teacher'),
        content: Text('Are you sure you want to remove "${teacher['name'] ?? 'Unnamed Teacher'}" from the list?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: Text('Remove', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
    
    if (result == true) {
      setState(() { _teachers.removeAt(idx); });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Teacher removed successfully')),
      );
    }
  }

  String _formatDateTime(String isoString) {
    try {
      final dateTime = DateTime.parse(isoString);
      return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour}:${dateTime.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return isoString;
    }
  }

  Future<void> _selectDate() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(2020),
      lastDate: DateTime.now().add(Duration(days: 365)),
    );
    if (picked != null) {
      setState(() {
        _dateController.text = '${picked.day.toString().padLeft(2, '0')}/${picked.month.toString().padLeft(2, '0')}/${picked.year}';
        formData.dateOfVisit = _dateController.text;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundColor,
      appBar: AppBar(
        title:  Text('BEF Site Verification Form', style: titleTextStyle(color: whiteColor)),
        backgroundColor: primaryColor,
        elevation: 0,
        automaticallyImplyLeading: false, // Removes the back button
      ),
      body: Center(
        child: SingleChildScrollView(
          child: Padding(
            padding: EdgeInsets.all(defaultPadding),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(containerRoundCorner)),
                    child: Padding(
                      padding: EdgeInsets.all(defaultPadding),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('1. Basic Site and Visit Information', style: titleTextStyle(size: 18, color: primaryColor, fontWeight: FontWeight.bold)),
                          Divider(),
                          _buildTextField('BEF Code as per record', (val) => formData.befCode = val, required: true),
                          
                          // Date picker field
                          InkWell(
                            onTap: _selectDate,
                            child: IgnorePointer(
                              child: TextFormField(
                                controller: _dateController,
                                decoration: InputDecoration(
                                  labelText: 'Date of Visit (DD/MM/YYYY) *',
                                  border: OutlineInputBorder(),
                                  suffixIcon: Icon(Icons.calendar_today),
                                ),
                                validator: (value) {
                                  if (value == null || value.isEmpty) {
                                    return 'Date of visit is required';
                                  }
                                  return null;
                                },
                              ),
                            ),
                          ),
                          SizedBox(height: 12),
                          
                          _buildTextField('Name of Proposed site/Village for New School', (val) => formData.proposedSite = val, required: true, maxLength: 200),
                          _buildTextField('Proposed School Name', (val) => formData.proposedSchoolName = val, required: true, maxLength: 200),
                          
                          // Add GPS coordinates section right after proposed school name
                          SizedBox(height: 8),
                          Container(
                            padding: EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.blue.shade50,
                              border: Border.all(color: Colors.blue.shade200),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('📍 Proposed Site GPS Coordinates', 
                                     style: TextStyle(fontWeight: FontWeight.bold, color: Colors.blue.shade700)),
                                SizedBox(height: 8),
                                Row(
                                  children: [
                                    Expanded(
                                      child: TextFormField(
                                        decoration: InputDecoration(
                                          labelText: 'Latitude (X)',
                                          border: OutlineInputBorder(),
                                          isDense: true,
                                        ),
                                        onChanged: (val) => formData.gpsProposedSiteX = val,
                                        keyboardType: TextInputType.numberWithOptions(decimal: true),
                                      ),
                                    ),
                                    SizedBox(width: 8),
                                    Expanded(
                                      child: TextFormField(
                                        decoration: InputDecoration(
                                          labelText: 'Longitude (Y)',
                                          border: OutlineInputBorder(),
                                          isDense: true,
                                        ),
                                        onChanged: (val) => formData.gpsProposedSiteY = val,
                                        keyboardType: TextInputType.numberWithOptions(decimal: true),
                                      ),
                                    ),
                                  ],
                                ),
                                SizedBox(height: 8),
                                SizedBox(
                                  width: double.infinity,
                                  child: ElevatedButton.icon(
                                    onPressed: _gettingLocation ? null : _getCurrentLocation,
                                    icon: _gettingLocation 
                                      ? SizedBox(
                                          width: 18, 
                                          height: 18, 
                                          child: CircularProgressIndicator(
                                            strokeWidth: 2,
                                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                                          ),
                                        ) 
                                      : Icon(Icons.my_location),
                                    label: Text(_gettingLocation ? 'Getting Location...' : 'Get Current Location'),
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: _gettingLocation ? Colors.grey : Colors.blue,
                                      foregroundColor: Colors.white,
                                      padding: EdgeInsets.symmetric(vertical: 12),
                                    ),
                                  ),
                                ),
                                if (formData.gpsProposedSiteX.isNotEmpty && formData.gpsProposedSiteY.isNotEmpty)
                                  Container(
                                    margin: EdgeInsets.only(top: 8),
                                    padding: EdgeInsets.all(8),
                                    decoration: BoxDecoration(
                                      color: Colors.green.shade50,
                                      border: Border.all(color: Colors.green),
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: Row(
                                      children: [
                                        Icon(Icons.check_circle, color: Colors.green, size: 16),
                                        SizedBox(width: 8),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Text('📍 Location Captured', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.green.shade700, fontSize: 12.0)),
                                              Text('Lat: ${formData.gpsProposedSiteX}, Lng: ${formData.gpsProposedSiteY}', style: TextStyle(fontSize: 11.0)),
                                            ],
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                              ],
                            ),
                          ),
                          SizedBox(height: 12),
                          
                          _buildTextField('District', (val) => formData.district = val, required: true),
                          _buildTextField('Tehsil', (val) => formData.tehsil = val, required: true),
                          _buildTextField('Union Council (UC)', (val) => formData.unionCouncil = val, required: true),
                          _buildTextField('Village Name', (val) => formData.villageName = val, required: true, maxLength: 200),
                          _buildNumberField('Distance from District HQ (KM)', (val) => formData.distanceFromHQ = val, required: true),
                          _buildTextField('Total Households (Proposed Site + Catchment Areas)', (val) => formData.totalHouseholds = val, required: true),
                          _buildDropdown('BEF School Functional Status', ['Yes', 'No'], (val) => formData.functionalStatus = val ?? '', required: true),
                          _buildTextField('If Non Functional : Reason', (val) => formData.nonFunctionalReason = val),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: 16),
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(containerRoundCorner)),
                    child: Padding(
                      padding: EdgeInsets.all(defaultPadding),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('2. GPS Coordinates and Nearby School Information', style: titleTextStyle(size: 18, color: primaryColor, fontWeight: FontWeight.bold)),
                          Divider(),
                          _buildTextField('GPS Coordinates of Existing Nearest GOVT School (X)', (val) => formData.gpsNearestSchoolX = val),
                          _buildTextField('GPS Coordinates of Existing Nearest GOVT School (Y)', (val) => formData.gpsNearestSchoolY = val),
                          _buildTextField('Nearest School BEMIS Code', (val) => formData.nearestSchoolBEMISCode = val),
                          _buildTextField('Nearest GOVT School Name', (val) => formData.nearestGovtSchoolName = val),
                          _buildDropdown('Nearest GOVT School Name Gender', ['Boys', 'Girls'], (val) => formData.nearestGovtSchoolGender = val ?? ''),
                          _buildDropdown('Level', ['Primary', 'Middle', 'High'], (val) => formData.nearestGovtSchoolLevel = val ?? ''),
                          _buildNumberField('Distance from Proposed Site (KM)', (val) => formData.distanceFromProposedSite = val),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: 16),
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(containerRoundCorner)),
                    child: Padding(
                      padding: EdgeInsets.all(defaultPadding),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('3. Population and OOSC (Ages 5–10)', style: titleTextStyle(size: 18, color: primaryColor, fontWeight: FontWeight.bold)),
                          Divider(),
                          _buildNumberField('Number of Out-of-School Children (OOSC) Boys', (val) => formData.ooscBoys = val),
                          _buildNumberField('Number of Out-of-School Children (OOSC) Girls', (val) => formData.ooscGirls = val),
                          _buildNumberField('Number of Out-of-School Children (OOSC) Total', (val) => formData.ooscTotal = val),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: 16),
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(containerRoundCorner)),
                    child: Padding(
                      padding: EdgeInsets.all(defaultPadding),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('4. Qualified Persons Available for Teaching in Area', style: titleTextStyle(size: 18, color: primaryColor, fontWeight: FontWeight.bold)),
                          Divider(),
                          
                          // Matric qualified persons
                          Text('Matric Qualified Persons', style: subTitleTextStyle(fontWeight: FontWeight.bold)),
                          SizedBox(height: 8),
                          Row(
                            children: [
                              Expanded(
                                child: _buildNumberField('Male', (val) => formData.qualifiedMatric = '${val}_${formData.qualifiedMatric.split('_').length > 1 ? formData.qualifiedMatric.split('_')[1] : ''}'),
                              ),
                              SizedBox(width: 12),
                              Expanded(
                                child: _buildNumberField('Female', (val) {
                                  final male = formData.qualifiedMatric.split('_')[0];
                                  formData.qualifiedMatric = '${male}_${val}';
                                }),
                              ),
                            ],
                          ),
                          SizedBox(height: 16),
                          
                          // FA/FSc qualified persons
                          Text('FA/FSc Qualified Persons', style: subTitleTextStyle(fontWeight: FontWeight.bold)),
                          SizedBox(height: 8),
                          Row(
                            children: [
                              Expanded(
                                child: _buildNumberField('Male', (val) => formData.qualifiedFAFSc = '${val}_${formData.qualifiedFAFSc.split('_').length > 1 ? formData.qualifiedFAFSc.split('_')[1] : ''}'),
                              ),
                              SizedBox(width: 12),
                              Expanded(
                                child: _buildNumberField('Female', (val) {
                                  final male = formData.qualifiedFAFSc.split('_')[0];
                                  formData.qualifiedFAFSc = '${male}_${val}';
                                }),
                              ),
                            ],
                          ),
                          SizedBox(height: 16),
                          
                          // BA/BSc qualified persons
                          Text('BA/BSc Qualified Persons', style: subTitleTextStyle(fontWeight: FontWeight.bold)),
                          SizedBox(height: 8),
                          Row(
                            children: [
                              Expanded(
                                child: _buildNumberField('Male', (val) => formData.qualifiedBABSc = '${val}_${formData.qualifiedBABSc.split('_').length > 1 ? formData.qualifiedBABSc.split('_')[1] : ''}'),
                              ),
                              SizedBox(width: 12),
                              Expanded(
                                child: _buildNumberField('Female', (val) {
                                  final male = formData.qualifiedBABSc.split('_')[0];
                                  formData.qualifiedBABSc = '${male}_${val}';
                                }),
                              ),
                            ],
                          ),
                          SizedBox(height: 16),
                          
                          // MA/MSc qualified persons
                          Text('MA/MSc Qualified Persons', style: subTitleTextStyle(fontWeight: FontWeight.bold)),
                          SizedBox(height: 8),
                          Row(
                            children: [
                              Expanded(
                                child: _buildNumberField('Male', (val) => formData.qualifiedMAMSc = '${val}_${formData.qualifiedMAMSc.split('_').length > 1 ? formData.qualifiedMAMSc.split('_')[1] : ''}'),
                              ),
                              SizedBox(width: 12),
                              Expanded(
                                child: _buildNumberField('Female', (val) {
                                  final male = formData.qualifiedMAMSc.split('_')[0];
                                  formData.qualifiedMAMSc = '${male}_${val}';
                                }),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: 16),
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(containerRoundCorner)),
                    child: Padding(
                      padding: EdgeInsets.all(defaultPadding),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('5. Qualified / Selected Teachers (If Any)', style: titleTextStyle(size: 18, color: primaryColor, fontWeight: FontWeight.bold)),
                          Divider(),
                          
                          // Single Teacher Fields (for backward compatibility)
                          Text('Primary Teacher Information', style: subTitleTextStyle(fontWeight: FontWeight.bold)),
                          _buildTextField('Teacher CNIC', (val) => formData.teacherCNIC = val),
                          _buildTextField('Teacher Name', (val) => formData.teacherName = val),
                          _buildTextField('Teacher Contact', (val) => formData.teacherContact = val),
                          _buildTextField('Teacher Qualification', (val) => formData.teacherQualification = val),
                          SizedBox(height: 16),
                          
                          // Multiple Teachers Section
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text('Additional Teachers', style: subTitleTextStyle(fontWeight: FontWeight.bold)),
                              Text('Total: ${_teachers.length}', style: TextStyle(color: Colors.grey[600])),
                            ],
                          ),
                          SizedBox(height: 8),
                          
                          // Teachers List
                          if (_teachers.isEmpty)
                            Container(
                              width: double.infinity,
                              padding: EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                border: Border.all(color: Colors.grey[300]!),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Column(
                                children: [
                                  Icon(Icons.group_add, color: Colors.grey[400], size: 48),
                                  SizedBox(height: 8),
                                  Text('No additional teachers added yet', 
                                    style: TextStyle(color: Colors.grey[600])),
                                ],
                              ),
                            )
                          else
                            ...(_teachers.asMap().entries.map((e) {
                              final idx = e.key;
                              final teacher = e.value;
                              return Card(
                                margin: EdgeInsets.only(bottom: 8),
                                elevation: 1,
                                child: ListTile(
                                  leading: CircleAvatar(
                                    backgroundColor: primaryColor,
                                    child: Text('${idx + 1}', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                                  ),
                                  title: Text(teacher['name'] ?? 'Unnamed Teacher', 
                                    style: TextStyle(fontWeight: FontWeight.bold)),
                                  subtitle: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      if ((teacher['qualification'] ?? '').isNotEmpty)
                                        Text('📚 ${teacher['qualification']}'),
                                      if ((teacher['cnic'] ?? '').isNotEmpty)
                                        Text('🆔 ${teacher['cnic']}'),
                                      if ((teacher['contact'] ?? '').isNotEmpty)
                                        Text('📞 ${teacher['contact']}'),
                                    ],
                                  ),
                                  trailing: IconButton(
                                    icon: Icon(Icons.delete, color: Colors.red), 
                                    onPressed: () => _showDeleteTeacherDialog(idx),
                                    tooltip: 'Remove Teacher',
                                  ),
                                ),
                              );
                            }).toList()),
                          
                          SizedBox(height: 12),
                          // Add Teacher Button
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton.icon(
                              onPressed: _addTeacher, 
                              icon: Icon(Icons.person_add), 
                              label: Text('Add New Teacher'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: primaryColor,
                                foregroundColor: Colors.white,
                                padding: EdgeInsets.symmetric(vertical: 12),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: 16),
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(containerRoundCorner)),
                    child: Padding(
                      padding: EdgeInsets.all(defaultPadding),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('6. Infrastructure and Facilities', style: titleTextStyle(size: 18, color: primaryColor, fontWeight: FontWeight.bold)),
                          Divider(),
                          _buildDropdown('Building Structure', ['Kacha', 'Pakka'], (val) => formData.buildingStructure = val ?? ''),
                          _buildNumberField('Number of Existing/Allocated Rooms', (val) => formData.allocatedRooms = val),
                          _buildDropdown('Toilets', ['Yes', 'No'], (val) => formData.toilets = val ?? ''),
                          _buildNumberField('Space for New Rooms', (val) => formData.spaceForNewRooms = val),
                          _buildDropdown('Boundary Wall', ['Yes', 'No'], (val) => formData.boundaryWall = val ?? ''),
                          _buildDropdown('Boundary Wall Status', ['Kacha', 'Pakka'], (val) => formData.boundaryWallStatus = val ?? ''),
                          
                          // Multi-select furniture with count fields
                          SizedBox(height: 16),
                          Text('Furniture Availability', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                          SizedBox(height: 8),
                          ..._buildFurnitureSelections(),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: 16),
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(containerRoundCorner)),
                    child: Padding(
                      padding: EdgeInsets.all(defaultPadding),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('7. Current BEF Enrollment (If School Functional)', style: titleTextStyle(size: 18, color: primaryColor, fontWeight: FontWeight.bold)),
                          Divider(),
                          _buildTextField('Girls', (val) => formData.currentEnrollmentGirls = val),
                          _buildTextField('Boys', (val) => formData.currentEnrollmentBoys = val),
                          _buildTextField('Total', (val) => formData.currentEnrollmentTotal = val),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: 16),
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(containerRoundCorner)),
                    child: Padding(
                      padding: EdgeInsets.all(defaultPadding),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('8. Enrollment Class-wise (if applicable)', style: titleTextStyle(size: 18, color: primaryColor, fontWeight: FontWeight.bold)),
                          Divider(),
                          _buildTextField('Details/Attach Sheet', (val) => formData.remarks = val),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: 16),
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(containerRoundCorner)),
                    child: Padding(
                      padding: EdgeInsets.all(defaultPadding),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('9. Remarks of Visiting Official', style: titleTextStyle(size: 18, color: primaryColor, fontWeight: FontWeight.bold)),
                          Divider(),
                          _buildTextField('Remarks/Observations/Recommendations', (val) => formData.remarks = val),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: 16),
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(containerRoundCorner)),
                    child: Padding(
                      padding: EdgeInsets.all(defaultPadding),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('10. Verified By', style: titleTextStyle(size: 18, color: primaryColor, fontWeight: FontWeight.bold)),
                          Divider(),
                          _buildTextField('Name', (val) => formData.verifiedByName = val),
                          _buildTextField('Designation (DMC/DMA)', (val) => formData.verifiedByDesignation = val),
                          _buildTextField('District', (val) => formData.verifiedByDistrict = val),
                          _buildTextField('Contact #', (val) => formData.verifiedByContact = val),
                          _buildTextField('Date', (val) => formData.verifiedByDate = val),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: 24),
                  
                  // Action Buttons Section
                  Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(containerRoundCorner)),
                    child: Padding(
                      padding: EdgeInsets.all(defaultPadding),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Form Actions', style: titleTextStyle(size: 18, color: primaryColor, fontWeight: FontWeight.bold)),
                          Divider(),
                          
                          if (isLoading) 
                            Center(child: CircularProgressIndicator())
                          else ...[
                            // Save Locally Button
                            CustomBtn(
                              text: 'Save Locally',
                              icon: Icons.save,
                              onPressed: _saveLocally,
                            ),
                            SizedBox(height: 12),
                            
                            // Export and Upload Row
                            Row(
                              children: [
                                Expanded(
                                  child: CustomBtn(
                                    color: secondaryColor,
                                    text: 'Export CSV',
                                    icon: Icons.file_download,
                                    onPressed: _exportToCsv,
                                  ),
                                ),
                                SizedBox(width: 8),
                                Expanded(
                                  child: formData.isUploaded 
                                    ? CustomBtn(
                                        color: Colors.grey,
                                        text: 'Already Uploaded ✓',
                                        icon: Icons.cloud_done,
                                        onPressed: null, // Disabled
                                      )
                                    : CustomBtn(
                                        color: const Color(0xFF388E3C),
                                        text: 'Upload to Sheets',
                                        icon: Icons.cloud_upload,
                                        onPressed: _uploadToGoogleSheets,
                                      ),
                                ),
                              ],
                            ),
                            
                            // Upload Status Info
                            if (formData.isUploaded && formData.uploadedAt != null)
                              Container(
                                margin: EdgeInsets.only(top: 8),
                                padding: EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: Colors.green.shade50,
                                  border: Border.all(color: Colors.green.shade200),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Row(
                                  children: [
                                    Icon(Icons.check_circle, color: Colors.green, size: 20),
                                    SizedBox(width: 8),
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            'Form uploaded successfully!',
                                            style: TextStyle(fontWeight: FontWeight.bold, color: Colors.green.shade700),
                                          ),
                                          Text(
                                            'Uploaded: ${_formatDateTime(formData.uploadedAt!)}',
                                            style: TextStyle(fontSize: 12.0, color: Colors.green.shade600),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            SizedBox(height: 12),
                            
                            // View Saved Forms Button
                            CustomBtn(
                              color: Colors.grey.shade700,
                              text: 'View Saved Forms',
                              icon: Icons.list_alt,
                              onPressed: () => Navigator.pushNamed(context, '/saved_forms'),
                            ),
                          ],
                          
                          if (error.isNotEmpty)
                            Padding(
                              padding: const EdgeInsets.only(top: 12),
                              child: Container(
                                padding: EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: Colors.red.shade50,
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: Colors.red.shade200),
                                ),
                                child: Row(
                                  children: [
                                    Icon(Icons.error, color: Colors.red, size: 20),
                                    SizedBox(width: 8),
                                    Expanded(child: Text(error, style: TextStyle(color: Colors.red.shade700))),
                                  ],
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTextField(String label, Function(String) onChanged, {bool required = false, int? maxLength}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Text(label, style: subTitleTextStyle()),
          ),
          InputField(
            hintText: label,
            onChanged: onChanged,
            maxLength: maxLength,
            validator: required ? (val) => val == null || val.isEmpty ? 'Required' : null : null,
          ),
        ],
      ),
    );
  }

  Widget _buildNumberField(String label, Function(String) onChanged, {bool required = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Text(label, style: subTitleTextStyle()),
          ),
          TextFormField(
            decoration: InputDecoration(
              hintText: label,
              border: OutlineInputBorder(),
              filled: true,
              fillColor: greyColor,
            ),
            keyboardType: TextInputType.numberWithOptions(decimal: true),
            onChanged: onChanged,
            validator: required ? (val) => val == null || val.isEmpty ? 'Required' : null : null,
          ),
        ],
      ),
    );
  }

  Widget _buildDropdown(String label, List<String> items, Function(String?) onChanged, {bool required = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Text(label, style: subTitleTextStyle()),
          ),
          Container(
            decoration: BoxDecoration(
              color: greyColor,
              borderRadius: BorderRadius.circular(containerRoundCorner),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: DropdownButtonFormField<String>(
              decoration: const InputDecoration(border: InputBorder.none),
              items: items.map((item) => DropdownMenuItem(value: item, child: Text(item))).toList(),
              onChanged: onChanged,
              validator: required ? (val) => val == null || val.isEmpty ? 'Required' : null : null,
            ),
          ),
        ],
      ),
    );
  }

  List<Widget> _buildFurnitureSelections() {
    List<Widget> widgets = [];
    
    furnitureSelections.forEach((furnitureType, isSelected) {
      widgets.add(
        Row(
          children: [
            Checkbox(
              value: isSelected,
              onChanged: (bool? value) {
                setState(() {
                  furnitureSelections[furnitureType] = value ?? false;
                });
              },
            ),
            Expanded(
              flex: 2,
              child: Text(furnitureType, style: TextStyle(fontSize: 16)),
            ),
            if (isSelected) ...[
              SizedBox(width: 10),
              Expanded(
                flex: 1,
                child: Container(
                  height: 50,
                  child: TextFormField(
                    controller: furnitureCountControllers[furnitureType],
                    decoration: InputDecoration(
                      labelText: 'Count',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                    ),
                    keyboardType: TextInputType.number,
                    onChanged: (value) {
                      // Update the form data based on furniture type
                      switch (furnitureType) {
                        case 'Chairs':
                          formData.furnitureChairs = value;
                          break;
                        case 'Tables':
                          formData.furnitureTable = value;
                          break;
                        case 'Tat':
                          formData.furnitureTat = value;
                          break;
                      }
                    },
                  ),
                ),
              ),
            ],
          ],
        ),
      );
      widgets.add(SizedBox(height: 8));
    });
    
    return widgets;
  }

  // ...existing code...
}
