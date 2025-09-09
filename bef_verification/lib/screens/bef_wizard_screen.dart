import 'package:flutter/material.dart';
import '../models/bef_form_model.dart';
import '../utils/constants.dart';
import '../utils/style.dart';
import '../widgets/input_field.dart';
import '../widgets/custom_btn.dart';
import '../services/sqlite_service.dart';
import 'package:geolocator/geolocator.dart';
import '../services/auth_service.dart';
import '../models/user_model.dart';

class BEFWizardScreen extends StatefulWidget {
  const BEFWizardScreen({super.key});

  @override
  State<BEFWizardScreen> createState() => _BEFWizardScreenState();
}

class _BEFWizardScreenState extends State<BEFWizardScreen> {
  final PageController _controller = PageController();
  final _formKeys = [GlobalKey<FormState>(), GlobalKey<FormState>(), GlobalKey<FormState>(), GlobalKey<FormState>(), GlobalKey<FormState>()];
  final BEFFormModel formData = BEFFormModel();
  int _current = 0;
  bool _saving = false;
  String _error = '';
  final AuthService _auth = AuthService();
  UserModel? _profile;

  // UI state
  String _functional = '';
  bool _furnitureChairs = false;
  bool _furnitureTable = false;
  bool _furnitureTat = false;
  
  // District and Tehsil selection
  String? _selectedDistrict;
  String? _selectedTehsil;
  
  // Teachers list
  List<Map<String, String>> _teachers = [];
  
  // Furniture count controllers
  final TextEditingController _chairsCountController = TextEditingController();
  final TextEditingController _tablesCountController = TextEditingController();
  final TextEditingController _tatCountController = TextEditingController();

  // District and Tehsil data
  final Map<String, List<String>> _districtTehsilMap = {
    'AWARAN': ['AWARAN', 'GISHKORE', 'JHALJAOO', 'MASHKAI'],
    'BARKHAN': ['BARKHAN'],
    'CHAGHI': ['DALBANDIN', 'NOKUNDI', 'TAFTAN'],
    'CHAMAN': ['CHAMAN'],
    'DERA BUGTI': ['DERA BUGTI', 'PHELLAWAGH', 'PHELLAWGH', 'PHELLAWGHE', 'SUI'],
    'DUKI': ['DUKI'],
    'GWADAR': ['GWADAR', 'JIWANI', 'ORMARA', 'PASNI'],
    'HARNAI': ['HARNAI', 'SHAHRIGH'],
    'HUB': ['DUREJI', 'GADDANI', 'HUB', 'LAKHRA', 'SOONMIANI (WINDER)', 'JAFER ABAD'],
    'JHAT PAT': ['JHATPAT'],
    'JHAL MAGSI': ['GANDAWAH', 'JHAL MAGSI'],
    'KACHHI': ['BHAG', 'DHADAR', 'KACHHI', 'MACH', 'SANNI'],
    'KALAT': ['KALAT', 'KHALIQABAD', 'MANGOCHAR'],
    'KECH': ['BULEDA', 'DASHT', 'DASTH', 'KECH', 'MAND', 'TUMP', 'TURBAT'],
    'KHARAN': ['KHARAN'],
    'KHUZDAR': ['KHUZDAR', 'MOOLA', 'NAL', 'WADH', 'ZEHRI'],
    'KILLA ABDULLAH': ['CHAMAN', 'DOBANDI', 'GULISTAN', 'KILLA ABDULLAH'],
    'KILLA SAIFULLAH': ['KILLA SAIFULLAH', 'MUSLIM BAGH'],
    'KOHLU': ['KAHAN', 'KOHLU', 'MAWAND'],
    'LASBELA': ['BELA', 'KANRAJ', 'LAKHRA', 'LEYARI', 'LIARI', 'UTHAL'],
    'LORALAI': ['BORI', 'MEKHTAR'],
    'MASTUNG': ['DASHT SPEZAND', 'KIRDGAP', 'MASTUNG'],
    'MUSAKHEL': ['Drug', 'DURUG', 'KINGRI', 'MUSAKHEL', 'Toi Ser'],
    'NASEER ABAD': ['BABA KOT', 'CHATTER', 'D.M.JAMALI', 'DERA MURAD JAMALI', 'GHAFOOR ABAD', 'GHAFOORABAD', 'TAMBOO'],
    'NOSHKI': ['NOSHKI'],
    'PANJGUR': ['GWARGO', 'PANJGUR', 'PAROOM'],
    'PISHIN': ['BARSHORE', 'HURAMZAI', 'KAREZAT', 'PISHIN', 'SARANAN'],
    'QUETTA': ['CHILTAN', 'ZARGHOON'],
    'SHERANI': ['SHERANI'],
    'SIBI': ['LEHRI', 'SIBI'],
    'SOHBAT PUR': ['Fareed Abad', 'Hair Din', 'Hairden', 'Hairdin', 'Manjhi pur', 'Panhwa', 'PANHWAR', 'Saeed Mohammad Kanrani', 'Saeed Muhammad', 'SAEED MUHAMMAD Kandrani', 'Saeed Muhammad KANRAN', 'Saeed Muhammad Kanrani', 'Saeed Muhammaf', 'SOHBAT PUR'],
    'SURAB': ['GIDDER', 'KALAT', 'SURAB'],
    'USTA MUHAMMAD': ['GANDAKHA', 'USTA MUHAMMAD'],
    'WASHUK': ['BASIMA', 'MASHKHEL', 'WASHUK'],
    'ZHOB': ['KAKAR KHURASAN', 'ZHOB'],
    'ZIARAT': ['SINJAVI', 'ZIARAT'],
  };

  @override
  void initState() {
    super.initState();
    _loadProfile();
    
    // Set current date as default
    final now = DateTime.now();
    formData.dateOfVisit = '${now.day.toString().padLeft(2, '0')}/${now.month.toString().padLeft(2, '0')}/${now.year}';
  }

  @override
  void dispose() {
    _chairsCountController.dispose();
    _tablesCountController.dispose();
    _tatCountController.dispose();
    super.dispose();
  }

  Future<void> _loadProfile() async {
    try {
      final p = await _auth.fetchCurrentUserProfile();
      setState(() {
        _profile = p;
        if (p != null) {
          formData.verifiedByName = '${p.firstName} ${p.lastName}'.trim();
          formData.verifiedByDesignation = p.designation;
          formData.verifiedByDistrict = p.district;
          formData.verifiedByContact = p.phoneNumber;
        }
      });
    } catch (_) {}
  }

  Future<void> _getLocation(void Function(Position) onPos) async {
    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    if (permission == LocationPermission.deniedForever || permission == LocationPermission.denied) {
      setState(() => _error = 'Location permission denied');
      return;
    }
    final pos = await Geolocator.getCurrentPosition(desiredAccuracy: LocationAccuracy.high);
    onPos(pos);
    setState(() {});
  }

  void _next() {
    if (_formKeys[_current].currentState?.validate() ?? true) {
      if (_current < _formKeys.length - 1) {
        setState(() => _current += 1);
        _controller.nextPage(duration: const Duration(milliseconds: 250), curve: Curves.easeInOut);
      }
    }
  }

  void _prev() {
    if (_current > 0) {
      setState(() => _current -= 1);
      _controller.previousPage(duration: const Duration(milliseconds: 250), curve: Curves.easeInOut);
    }
  }

  Future<void> _finish() async {
    if (!(_formKeys[_current].currentState?.validate() ?? true)) return;
    // Encode furniture multi-select into model
    formData.furnitureChairs = _furnitureChairs ? (_chairsCountController.text.isNotEmpty ? _chairsCountController.text : '1') : '';
    formData.furnitureTable = _furnitureTable ? (_tablesCountController.text.isNotEmpty ? _tablesCountController.text : '1') : '';
    formData.furnitureTat = _furnitureTat ? (_tatCountController.text.isNotEmpty ? _tatCountController.text : '1') : '';
    
    // Add teachers data
    formData.teachers = _teachers;
    
    setState(() { _saving = true; _error = ''; });
    try {
      await SqliteService.saveForm(formData);
      if (!mounted) return;
      setState(() { _saving = false; });
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Saved locally!')));
      Navigator.pop(context);
    } catch (e) {
      setState(() { _saving = false; _error = e.toString(); });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('New Verification', style: titleTextStyle(color: whiteColor)),
        backgroundColor: primaryColor,
        elevation: 0,
        automaticallyImplyLeading: false, // Removes the back button
      ),
      backgroundColor: backgroundColor,
      body: Column(
        children: [
          Padding(
            padding: EdgeInsets.all(defaultPadding),
            child: Row(
              children: List.generate(_formKeys.length, (i) => Expanded(
                child: Container(
                  height: 6,
                  margin: EdgeInsets.symmetric(horizontal: 4),
                  decoration: BoxDecoration(
                    color: i <= _current ? primaryColor : greyColor,
                    borderRadius: BorderRadius.circular(999),
                  ),
                ),
              )),
            ),
          ),
          Expanded(
            child: PageView(
              controller: _controller,
              physics: const NeverScrollableScrollPhysics(),
              children: [
                _stepCard('1. Basic Site Info', _formKeys[0], [
                  _labeled('BEF Code as per record', (v) => formData.befCode = v, required: true),
                  _dateLabeled('Date of Visit', (v) => formData.dateOfVisit = v),
                  _labeled('Proposed site/Village', (v) => formData.proposedSite = v, required: true, maxLength: 200),
                  _labeled('Proposed School Name', (v) => formData.proposedSchoolName = v, required: true, maxLength: 200),
                  _gpsLabeled('GPS Proposed Site (X,Y)',
                    onGet: () => _getLocation((pos) { formData.gpsProposedSiteX = pos.latitude.toStringAsFixed(6); formData.gpsProposedSiteY = pos.longitude.toStringAsFixed(6); }),
                    display: () => '${formData.gpsProposedSiteX}, ${formData.gpsProposedSiteY}'
                  ),
                  _districtDropdown(),
                  _tehsilDropdown(),
                  _labeled('Union Council (UC)', (v) => formData.unionCouncil = v, required: true),
                  _labeled('Village Name', (v) => formData.villageName = v, required: true, maxLength: 200),
                ]),
                _stepCard('2. Distances & Households', _formKeys[1], [
                  _numberLabeled('Distance from District HQ (KM)', (v) => formData.distanceFromHQ = v, required: true),
                  _labeled('Total Households (Site + Catchment)', (v) => formData.totalHouseholds = v, required: true),
                  _dropdownLabeled('BEF School Functional Status', ['Yes','No'], (v) { setState(() { _functional = v ?? ''; formData.functionalStatus = v ?? ''; }); }, required: true),
                  if (_functional == 'No') _labeled('If Non Functional : Reason', (v) => formData.nonFunctionalReason = v),
                ]),
                _stepCard('3. GPS & Nearest School', _formKeys[2], [
                  _gpsLabeled('GPS Nearest GOVT School (X,Y)',
                    onGet: () => _getLocation((pos) { formData.gpsNearestSchoolX = pos.latitude.toStringAsFixed(6); formData.gpsNearestSchoolY = pos.longitude.toStringAsFixed(6); }),
                    display: () => '${formData.gpsNearestSchoolX}, ${formData.gpsNearestSchoolY}'
                  ),
                  _labeled('Nearest School BEMIS Code', (v) => formData.nearestSchoolBEMISCode = v),
                  _labeled('Nearest GOVT School Name', (v) => formData.nearestGovtSchoolName = v),
                  _dropdownLabeled('Nearest GOVT School Gender', ['Boys','Girls'], (v) => formData.nearestGovtSchoolGender = v ?? ''),
                  _dropdownLabeled('Level', ['Primary','Middle','High'], (v) => formData.nearestGovtSchoolLevel = v ?? ''),
                  _numberLabeled('Distance from Proposed Site (KM)', (v) => formData.distanceFromProposedSite = v),
                ]),
                _stepCard('4. OOSC & Qualified Persons', _formKeys[3], [
                  _numberLabeled('OOSC Boys', (v) { formData.ooscBoys = v; _updateOoscTotal(); }),
                  _numberLabeled('OOSC Girls', (v) { formData.ooscGirls = v; _updateOoscTotal(); }),
                  _readonlyLabeled('OOSC Total', () => formData.ooscTotal),
                  Padding(
                    padding: const EdgeInsets.only(top: 8, bottom: 6),
                    child: Text('Qualified Persons Available for Teaching in Area', style: titleTextStyle(size: 16, color: primaryColor, fontWeight: FontWeight.bold)),
                  ),
                  _qualifiedPersonRow('Matric', 
                    onMaleChanged: (v) => _updateQualifiedCount('matric', 'male', v),
                    onFemaleChanged: (v) => _updateQualifiedCount('matric', 'female', v)
                  ),
                  _qualifiedPersonRow('FA/FSc', 
                    onMaleChanged: (v) => _updateQualifiedCount('fafsc', 'male', v),
                    onFemaleChanged: (v) => _updateQualifiedCount('fafsc', 'female', v)
                  ),
                  _qualifiedPersonRow('BA/BSc', 
                    onMaleChanged: (v) => _updateQualifiedCount('babsc', 'male', v),
                    onFemaleChanged: (v) => _updateQualifiedCount('babsc', 'female', v)
                  ),
                  _qualifiedPersonRow('MA/MSc', 
                    onMaleChanged: (v) => _updateQualifiedCount('mamsc', 'male', v),
                    onFemaleChanged: (v) => _updateQualifiedCount('mamsc', 'female', v)
                  ),
                  Padding(
                    padding: const EdgeInsets.only(top: 16, bottom: 6),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Teachers', style: titleTextStyle(size: 16, color: primaryColor, fontWeight: FontWeight.bold)),
                        Text('Total: ${_teachers.length}', style: TextStyle(color: Colors.grey[600])),
                      ],
                    ),
                  ),
                  _teachersList(),
                  SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _addTeacher,
                      icon: Icon(Icons.person_add, color: Colors.white),
                      label: Text('Add Teacher', style: TextStyle(color: Colors.white)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: primaryColor,
                        padding: EdgeInsets.symmetric(vertical: 12),
                      ),
                    ),
                  ),
                ]),
                _stepCard('5. Infrastructure, Furniture & Verified By', _formKeys[4], [
                  _dropdownLabeled('Building Structure', ['Kacha','Pakka'], (v) => formData.buildingStructure = v ?? ''),
                  _numberLabeled('Existing/Allocated Rooms', (v) => formData.allocatedRooms = v),
                  _dropdownLabeled('Toilets', ['Yes','No'], (v) => formData.toilets = v ?? ''),
                  _numberLabeled('Space for New Rooms', (v) => formData.spaceForNewRooms = v),
                  _dropdownLabeled('Boundary Wall', ['Yes','No'], (v) => formData.boundaryWall = v ?? ''),
                  _dropdownLabeled('Boundary Wall Status', ['Kacha','Pakka'], (v) => formData.boundaryWallStatus = v ?? ''),
                  Padding(
                    padding: const EdgeInsets.only(top: 8, bottom: 6),
                    child: Text('Furniture (multi-select)', style: titleTextStyle(size: 16, color: primaryColor, fontWeight: FontWeight.bold)),
                  ),
                  _multiFurniture(),
                  _labeled('Remarks', (v) => formData.remarks = v),
                  Padding(
                    padding: const EdgeInsets.only(top: 8, bottom: 6),
                    child: Text('Verified By (auto-filled from profile)', style: titleTextStyle(size: 16, color: primaryColor, fontWeight: FontWeight.bold)),
                  ),
                  _readonlyLabeled('Name', () => formData.verifiedByName),
                  _readonlyLabeled('Designation', () => formData.verifiedByDesignation),
                  _readonlyLabeled('District', () => formData.verifiedByDistrict),
                  _readonlyLabeled('Contact #', () => formData.verifiedByContact),
                  _dateLabeled('Date', (v) => formData.verifiedByDate = v),
                ]),
              ],
            ),
          ),
          if (_error.isNotEmpty) Padding(padding: const EdgeInsets.only(bottom: 8), child: Text(_error, style: const TextStyle(color: Colors.red))),
          Padding(
            padding: EdgeInsets.all(defaultPadding),
            child: Row(
              children: [
                Expanded(child: CustomBtn(text: 'Previous', color: secondaryColor, onPressed: _current == 0 || _saving ? null : _prev)),
                const SizedBox(width: 12),
                Expanded(child: CustomBtn(text: _current == _formKeys.length - 1 ? 'Finish' : 'Next', onPressed: _saving ? null : (_current == _formKeys.length - 1 ? _finish : _next))),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _updateOoscTotal() {
    final b = int.tryParse(formData.ooscBoys) ?? 0;
    final g = int.tryParse(formData.ooscGirls) ?? 0;
    setState(() => formData.ooscTotal = (b + g).toString());
  }

  Widget _stepCard(String title, GlobalKey<FormState> key, List<Widget> fields) {
    return Padding(
      padding: EdgeInsets.all(defaultPadding),
      child: Card(
        elevation: 2,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(containerRoundCorner)),
        child: Padding(
          padding: EdgeInsets.all(defaultPadding),
          child: Form(
            key: key,
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(title, style: titleTextStyle(size: 18, color: primaryColor, fontWeight: FontWeight.bold)),
                  const Divider(),
                  ...fields,
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _labeled(String label, Function(String) onChanged, {bool required = false, int? maxLength}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(padding: const EdgeInsets.only(bottom: 6), child: Text(label, style: subTitleTextStyle())),
          InputField(
            hintText: label, 
            onChanged: onChanged, 
            maxLength: maxLength,
            validator: required ? (v) => v == null || v.isEmpty ? 'Required' : null : null
          ),
        ],
      ),
    );
  }

  Widget _numberLabeled(String label, Function(String) onChanged, {bool required = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(padding: const EdgeInsets.only(bottom: 6), child: Text(label, style: subTitleTextStyle())),
          InputField(hintText: label, 
            onChanged: onChanged, 
             inputType: TextInputType.numberWithOptions(decimal: true),
            validator: required ? (val) => val == null || val.isEmpty ? 'Required' : null : null,)
          
        ],
      ),
    );
  }

  Widget _readonlyLabeled(String label, String Function() getValue) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(padding: const EdgeInsets.only(bottom: 6), child: Text(label, style: subTitleTextStyle())),
          Container(
            decoration: BoxDecoration(color: greyColor, borderRadius: BorderRadius.circular(containerRoundCorner)),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
            child: Text(getValue(), style: titleTextStyle(size: 16)),
          ),
        ],
      ),
    );
  }

  Widget _dateLabeled(String label, Function(String) onChanged) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(padding: const EdgeInsets.only(bottom: 6), child: Text(label, style: subTitleTextStyle())),
          GestureDetector(
            onTap: () async { 
              final DateTime? picked = await showDatePicker(
                context: context,
                initialDate: DateTime.now(),
                firstDate: DateTime(2020),
                lastDate: DateTime.now().add(Duration(days: 365)),
              );
              if (picked != null) {
                final dateString = '${picked.day.toString().padLeft(2, '0')}/${picked.month.toString().padLeft(2, '0')}/${picked.year}';
                setState(() {
                  formData.dateOfVisit = dateString;
                });
                onChanged(dateString);
              }
            },
            child: Container(
              decoration: BoxDecoration(color: greyColor, borderRadius: BorderRadius.circular(containerRoundCorner)),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(formData.dateOfVisit.isNotEmpty ? formData.dateOfVisit : 'Select date', style: titleTextStyle(size: 16)),
                  const Icon(Icons.calendar_today, size: 18),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _gpsLabeled(String label, {required VoidCallback onGet, required String Function() display}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(padding: const EdgeInsets.only(bottom: 6), child: Text(label, style: subTitleTextStyle())),
          Row(
            children: [
              Expanded(
                child: Container(
                  decoration: BoxDecoration(color: greyColor, borderRadius: BorderRadius.circular(containerRoundCorner)),
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
                  child: Text(display(), style: titleTextStyle(size: 16)),
                ),
              ),
              const SizedBox(width: 8),
              CustomBtn(text: 'Get', width: 90, onPressed: onGet),
            ],
          ),
        ],
      ),
    );
  }

  Widget _dropdownLabeled(String label, List<String> items, Function(String?) onChanged, {bool required = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(padding: const EdgeInsets.only(bottom: 6), child: Text(label, style: subTitleTextStyle())),
          Container(
            decoration: BoxDecoration(color: greyColor, borderRadius: BorderRadius.circular(containerRoundCorner)),
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: DropdownButtonFormField<String>(
              decoration: const InputDecoration(border: InputBorder.none),
              items: items.map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
              onChanged: onChanged,
              validator: required ? (val) => val == null || val.isEmpty ? 'Required' : null : null,
            ),
          ),
        ],
      ),
    );
  }

  Widget _multiFurniture() {
    return Column(
      children: [
        Row(
          children: [
            Checkbox(
              value: _furnitureChairs,
              onChanged: (v) => setState(() => _furnitureChairs = v ?? false),
            ),
            Expanded(flex: 2, child: Text('Chairs', style: TextStyle(fontSize: 16))),
            if (_furnitureChairs) ...[
              SizedBox(width: 10),
              Expanded(
                flex: 1,
                child: Container(
                  height: 50,
                  child: TextFormField(
                    controller: _chairsCountController,
                    decoration: InputDecoration(
                      labelText: 'Count',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                    ),
                    keyboardType: TextInputType.number,
                    onChanged: (value) => formData.furnitureChairs = value,
                  ),
                ),
              ),
            ],
          ],
        ),
        Row(
          children: [
            Checkbox(
              value: _furnitureTable,
              onChanged: (v) => setState(() => _furnitureTable = v ?? false),
            ),
            Expanded(flex: 2, child: Text('Tables', style: TextStyle(fontSize: 16))),
            if (_furnitureTable) ...[
              SizedBox(width: 10),
              Expanded(
                flex: 1,
                child: Container(
                  height: 50,
                  child: TextFormField(
                    controller: _tablesCountController,
                    decoration: InputDecoration(
                      labelText: 'Count',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                    ),
                    keyboardType: TextInputType.number,
                    onChanged: (value) => formData.furnitureTable = value,
                  ),
                ),
              ),
            ],
          ],
        ),
        Row(
          children: [
            Checkbox(
              value: _furnitureTat,
              onChanged: (v) => setState(() => _furnitureTat = v ?? false),
            ),
            Expanded(flex: 2, child: Text('Tat', style: TextStyle(fontSize: 16))),
            if (_furnitureTat) ...[
              SizedBox(width: 10),
              Expanded(
                flex: 1,
                child: Container(
                  height: 50,
                  child: TextFormField(
                    controller: _tatCountController,
                    decoration: InputDecoration(
                      labelText: 'Count',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                    ),
                    keyboardType: TextInputType.number,
                    onChanged: (value) => formData.furnitureTat = value,
                  ),
                ),
              ),
            ],
          ],
        ),
      ],
    );
  }

  // Helper method for qualified person rows
  Widget _qualifiedPersonRow(String title, {required Function(String) onMaleChanged, required Function(String) onFemaleChanged}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: subTitleTextStyle(fontWeight: FontWeight.bold)),
          SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Male', style: TextStyle(fontSize: 14)),
                    SizedBox(height: 4),
                    InputField(hintText: '',inputType: TextInputType.number,
                      onChanged: onMaleChanged,)
                    
                  ],
                ),
              ),
              SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Female', style: TextStyle(fontSize: 14)),
                    SizedBox(height: 4),
                    InputField(hintText: '',inputType: TextInputType.number,
                      onChanged: onMaleChanged,)
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // Update qualified count helper
  void _updateQualifiedCount(String type, String gender, String value) {
    switch (type) {
      case 'matric':
        final parts = formData.qualifiedMatric.split('_');
        if (gender == 'male') {
          formData.qualifiedMatric = '${value}_${parts.length > 1 ? parts[1] : ''}';
        } else {
          formData.qualifiedMatric = '${parts.isNotEmpty ? parts[0] : ''}_${value}';
        }
        break;
      case 'fafsc':
        final parts = formData.qualifiedFAFSc.split('_');
        if (gender == 'male') {
          formData.qualifiedFAFSc = '${value}_${parts.length > 1 ? parts[1] : ''}';
        } else {
          formData.qualifiedFAFSc = '${parts.isNotEmpty ? parts[0] : ''}_${value}';
        }
        break;
      case 'babsc':
        final parts = formData.qualifiedBABSc.split('_');
        if (gender == 'male') {
          formData.qualifiedBABSc = '${value}_${parts.length > 1 ? parts[1] : ''}';
        } else {
          formData.qualifiedBABSc = '${parts.isNotEmpty ? parts[0] : ''}_${value}';
        }
        break;
      case 'mamsc':
        final parts = formData.qualifiedMAMSc.split('_');
        if (gender == 'male') {
          formData.qualifiedMAMSc = '${value}_${parts.length > 1 ? parts[1] : ''}';
        } else {
          formData.qualifiedMAMSc = '${parts.isNotEmpty ? parts[0] : ''}_${value}';
        }
        break;
    }
  }

  // Teachers list widget
  Widget _teachersList() {
    if (_teachers.isEmpty) {
      return Container(
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
            Text('No teachers added yet', style: TextStyle(color: Colors.grey[600])),
          ],
        ),
      );
    }

    return Column(
      children: _teachers.asMap().entries.map((e) {
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
            title: Text(teacher['name'] ?? 'Unnamed Teacher', style: TextStyle(fontWeight: FontWeight.bold)),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if ((teacher['qualification'] ?? '').isNotEmpty) Text('📚 ${teacher['qualification']}'),
                if ((teacher['cnic'] ?? '').isNotEmpty) Text('🆔 ${teacher['cnic']}'),
                if ((teacher['contact'] ?? '').isNotEmpty) Text('📞 ${teacher['contact']}'),
              ],
            ),
            trailing: IconButton(
              icon: Icon(Icons.delete, color: Colors.red),
              onPressed: () => _removeTeacher(idx),
            ),
          ),
        );
      }).toList(),
    );
  }

  // Add teacher method
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

  // Remove teacher method
  void _removeTeacher(int index) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Remove Teacher'),
        content: Text('Are you sure you want to remove this teacher?'),
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
      setState(() {
        _teachers.removeAt(index);
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Teacher removed successfully')),
      );
    }
  }

  // District dropdown widget
  Widget _districtDropdown() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Text('District *', style: subTitleTextStyle()),
          ),
          Container(
            decoration: BoxDecoration(
              color: greyColor,
              borderRadius: BorderRadius.circular(containerRoundCorner),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: DropdownButtonFormField<String>(
              decoration: const InputDecoration(border: InputBorder.none),
              hint: Text('Select District'),
              value: _selectedDistrict,
              items: _districtTehsilMap.keys.map((district) => 
                DropdownMenuItem(value: district, child: Text(district))
              ).toList(),
              onChanged: (value) {
                setState(() {
                  _selectedDistrict = value;
                  _selectedTehsil = null; // Reset tehsil when district changes
                  formData.district = value ?? '';
                  formData.tehsil = ''; // Clear tehsil in form data
                });
              },
              validator: (val) => val == null || val.isEmpty ? 'District is required' : null,
            ),
          ),
        ],
      ),
    );
  }

  // Tehsil dropdown widget
  Widget _tehsilDropdown() {
    final tehsilOptions = _selectedDistrict != null 
        ? _districtTehsilMap[_selectedDistrict!] ?? []
        : <String>[];

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Text('Tehsil *', style: subTitleTextStyle()),
          ),
          Container(
            decoration: BoxDecoration(
              color: _selectedDistrict == null ? Colors.grey[200] : greyColor,
              borderRadius: BorderRadius.circular(containerRoundCorner),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: DropdownButtonFormField<String>(
              decoration: const InputDecoration(border: InputBorder.none),
              hint: Text(_selectedDistrict == null ? 'Select District first' : 'Select Tehsil'),
              value: _selectedTehsil,
              items: tehsilOptions.isNotEmpty 
                  ? tehsilOptions.map((tehsil) => 
                      DropdownMenuItem(value: tehsil, child: Text(tehsil))
                    ).toList()
                  : [],
              onChanged: _selectedDistrict == null ? null : (value) {
                setState(() {
                  _selectedTehsil = value;
                  formData.tehsil = value ?? '';
                });
              },
              validator: (val) => val == null || val.isEmpty ? 'Tehsil is required' : null,
            ),
          ),
          if (_selectedDistrict == null)
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Text(
                'Please select a district first',
                style: TextStyle(color: Colors.grey[600], fontSize: 12),
              ),
            ),
        ],
      ),
    );
  }
} 