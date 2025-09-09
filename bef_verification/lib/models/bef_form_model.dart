import 'dart:convert';

class BEFFormModel {
  String befCode = '';
  // Add all other fields from the template here
  // Example:
  String dateOfVisit = '';
  String proposedSite = '';
  String proposedSchoolName = '';
  String district = '';
  String tehsil = '';
  String unionCouncil = '';
  String villageName = '';
  String distanceFromHQ = '';
  String totalHouseholds = '';
  String functionalStatus = '';
  String nonFunctionalReason = '';
  String gpsNearestSchoolX = '';
  String gpsNearestSchoolY = '';
  String gpsProposedSiteX = '';
  String gpsProposedSiteY = '';
  String nearestSchoolBEMISCode = '';
  String nearestGovtSchoolName = '';
  String nearestGovtSchoolGender = '';
  String nearestGovtSchoolLevel = '';
  String distanceFromProposedSite = '';
  String ooscBoys = '';
  String ooscGirls = '';
  String ooscTotal = '';
  String qualifiedMatric = '';
  String qualifiedFAFSc = '';
  String qualifiedBABSc = '';
  String qualifiedMAMSc = '';
  String teacherCNIC = '';
  String teacherName = '';
  String teacherContact = '';
  String teacherQualification = '';
  String buildingStructure = '';
  String allocatedRooms = '';
  String toilets = '';
  String spaceForNewRooms = '';
  String boundaryWall = '';
  String boundaryWallStatus = '';
  String furnitureChairs = '';
  String furnitureTable = '';
  String furnitureTat = '';
  String currentEnrollmentGirls = '';
  String currentEnrollmentBoys = '';
  String currentEnrollmentTotal = '';
  String remarks = '';
  String verifiedByName = '';
  String verifiedByDesignation = '';
  String verifiedByDistrict = '';
  String verifiedByContact = '';
  String verifiedByDate = '';
  List<Map<String, String>> teachers = [];
  bool isUploaded = false; // Track if form has been uploaded to Google Sheets
  String? uploadedAt; // Timestamp when uploaded

  Map<String, dynamic> toMap() {
    return {
      'befCode': befCode,
      'dateOfVisit': dateOfVisit,
      'proposedSite': proposedSite,
      'proposedSchoolName': proposedSchoolName,
      'district': district,
      'tehsil': tehsil,
      'unionCouncil': unionCouncil,
      'villageName': villageName,
      'distanceFromHQ': distanceFromHQ,
      'totalHouseholds': totalHouseholds,
      'functionalStatus': functionalStatus,
      'nonFunctionalReason': nonFunctionalReason,
      'gpsNearestSchoolX': gpsNearestSchoolX,
      'gpsNearestSchoolY': gpsNearestSchoolY,
      'gpsProposedSiteX': gpsProposedSiteX,
      'gpsProposedSiteY': gpsProposedSiteY,
      'nearestSchoolBEMISCode': nearestSchoolBEMISCode,
      'nearestGovtSchoolName': nearestGovtSchoolName,
      'nearestGovtSchoolGender': nearestGovtSchoolGender,
      'nearestGovtSchoolLevel': nearestGovtSchoolLevel,
      'distanceFromProposedSite': distanceFromProposedSite,
      'ooscBoys': ooscBoys,
      'ooscGirls': ooscGirls,
      'ooscTotal': ooscTotal,
      'qualifiedMatric': qualifiedMatric,
      'qualifiedFAFSc': qualifiedFAFSc,
      'qualifiedBABSc': qualifiedBABSc,
      'qualifiedMAMSc': qualifiedMAMSc,
      'teacherCNIC': teacherCNIC,
      'teacherName': teacherName,
      'teacherContact': teacherContact,
      'teacherQualification': teacherQualification,
      'buildingStructure': buildingStructure,
      'allocatedRooms': allocatedRooms,
      'toilets': toilets,
      'spaceForNewRooms': spaceForNewRooms,
      'boundaryWall': boundaryWall,
      'boundaryWallStatus': boundaryWallStatus,
      'furnitureChairs': furnitureChairs,
      'furnitureTable': furnitureTable,
      'furnitureTat': furnitureTat,
      'currentEnrollmentGirls': currentEnrollmentGirls,
      'currentEnrollmentBoys': currentEnrollmentBoys,
      'currentEnrollmentTotal': currentEnrollmentTotal,
      'remarks': remarks,
      'verifiedByName': verifiedByName,
      'verifiedByDesignation': verifiedByDesignation,
      'verifiedByDistrict': verifiedByDistrict,
      'verifiedByContact': verifiedByContact,
      'verifiedByDate': verifiedByDate,
      'teachers': teachers,
      'isUploaded': isUploaded ? 1 : 0, // SQLite doesn't have boolean, use int
      'uploadedAt': uploadedAt,
    };
  }

  static BEFFormModel fromMap(Map<String, dynamic> map) {
    final model = BEFFormModel();
    model.befCode = map['befCode']?.toString() ?? '';
    model.dateOfVisit = map['dateOfVisit']?.toString() ?? '';
    model.proposedSite = map['proposedSite']?.toString() ?? '';
    model.proposedSchoolName = map['proposedSchoolName']?.toString() ?? '';
    model.district = map['district']?.toString() ?? '';
    model.tehsil = map['tehsil']?.toString() ?? '';
    model.unionCouncil = map['unionCouncil']?.toString() ?? '';
    model.villageName = map['villageName']?.toString() ?? '';
    model.distanceFromHQ = map['distanceFromHQ']?.toString() ?? '';
    model.totalHouseholds = map['totalHouseholds']?.toString() ?? '';
    model.functionalStatus = map['functionalStatus']?.toString() ?? '';
    model.nonFunctionalReason = map['nonFunctionalReason']?.toString() ?? '';
    model.gpsNearestSchoolX = map['gpsNearestSchoolX']?.toString() ?? '';
    model.gpsNearestSchoolY = map['gpsNearestSchoolY']?.toString() ?? '';
    model.gpsProposedSiteX = map['gpsProposedSiteX']?.toString() ?? '';
    model.gpsProposedSiteY = map['gpsProposedSiteY']?.toString() ?? '';
    model.nearestSchoolBEMISCode = map['nearestSchoolBEMISCode']?.toString() ?? '';
    model.nearestGovtSchoolName = map['nearestGovtSchoolName']?.toString() ?? '';
    model.nearestGovtSchoolGender = map['nearestGovtSchoolGender']?.toString() ?? '';
    model.nearestGovtSchoolLevel = map['nearestGovtSchoolLevel']?.toString() ?? '';
    model.distanceFromProposedSite = map['distanceFromProposedSite']?.toString() ?? '';
    model.ooscBoys = map['ooscBoys']?.toString() ?? '';
    model.ooscGirls = map['ooscGirls']?.toString() ?? '';
    model.ooscTotal = map['ooscTotal']?.toString() ?? '';
    model.qualifiedMatric = map['qualifiedMatric']?.toString() ?? '';
    model.qualifiedFAFSc = map['qualifiedFAFSc']?.toString() ?? '';
    model.qualifiedBABSc = map['qualifiedBABSc']?.toString() ?? '';
    model.qualifiedMAMSc = map['qualifiedMAMSc']?.toString() ?? '';
    model.teacherCNIC = map['teacherCNIC']?.toString() ?? '';
    model.teacherName = map['teacherName']?.toString() ?? '';
    model.teacherContact = map['teacherContact']?.toString() ?? '';
    model.teacherQualification = map['teacherQualification']?.toString() ?? '';
    model.buildingStructure = map['buildingStructure']?.toString() ?? '';
    model.allocatedRooms = map['allocatedRooms']?.toString() ?? '';
    model.toilets = map['toilets']?.toString() ?? '';
    model.spaceForNewRooms = map['spaceForNewRooms']?.toString() ?? '';
    model.boundaryWall = map['boundaryWall']?.toString() ?? '';
    model.boundaryWallStatus = map['boundaryWallStatus']?.toString() ?? '';
    model.furnitureChairs = map['furnitureChairs']?.toString() ?? '';
    model.furnitureTable = map['furnitureTable']?.toString() ?? '';
    model.furnitureTat = map['furnitureTat']?.toString() ?? '';
    model.currentEnrollmentGirls = map['currentEnrollmentGirls']?.toString() ?? '';
    model.currentEnrollmentBoys = map['currentEnrollmentBoys']?.toString() ?? '';
    model.currentEnrollmentTotal = map['currentEnrollmentTotal']?.toString() ?? '';
    model.remarks = map['remarks']?.toString() ?? '';
    model.verifiedByName = map['verifiedByName']?.toString() ?? '';
    model.verifiedByDesignation = map['verifiedByDesignation']?.toString() ?? '';
    model.verifiedByDistrict = map['verifiedByDistrict']?.toString() ?? '';
    model.verifiedByContact = map['verifiedByContact']?.toString() ?? '';
    model.verifiedByDate = map['verifiedByDate']?.toString() ?? '';
    
    // Handle upload status
    model.isUploaded = (map['isUploaded'] == 1 || map['isUploaded'] == true);
    model.uploadedAt = map['uploadedAt']?.toString();
    
    // teachers may be a List<Map> or List<dynamic>
    final t = map['teachers'];
    if (t is List) {
      try {
        model.teachers = t.map((e) {
          if (e is Map) return Map<String, String>.from(e.map((k, v) => MapEntry(k.toString(), v?.toString() ?? '')));
          return <String, String>{};
        }).toList();
      } catch (_) {
        model.teachers = [];
      }
    }
    return model;
  }

  // JSON helpers for SQLite storage
  String toJson() => jsonEncode(toMap());

  static BEFFormModel fromJson(String jsonLike) {
    // Prefer proper JSON; but accept the older toString() map-like format as a fallback.
    try {
      final dynamic decoded = jsonDecode(jsonLike);
      if (decoded is Map<String, dynamic>) return BEFFormModel.fromMap(decoded);
    } catch (_) {}

    // Fallback: parse simple 'key: value' pairs as produced by Map.toString()
    final Map<String, dynamic> map = {};
    final RegExp pair = RegExp(r"'?(\w+)'?:\s*'?(.*?)'?(?:,|\})");
    for (final match in pair.allMatches(jsonLike)) {
      final key = match.group(1) ?? '';
      final value = match.group(2) ?? '';
      map[key] = value.trim();
    }
    return BEFFormModel.fromMap(map);
  }
}
