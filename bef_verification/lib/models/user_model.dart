class UserModel {
  final String firstName;
  final String lastName;
  final String phoneNumber;
  final String email;
  final String cnic;
  final String district;
  final String gender;
  final String designation;

  UserModel({
    required this.firstName,
    required this.lastName,
    required this.phoneNumber,
    required this.email,
    required this.cnic,
    required this.district,
    required this.gender,
    required this.designation,
  });

  Map<String, dynamic> toMap() {
    return {
      'firstName': firstName,
      'lastName': lastName,
      'phoneNumber': phoneNumber,
      'email': email,
      'cnic': cnic,
      'district': district,
      'gender': gender,
      'designation': designation,
    };
  }

  factory UserModel.fromMap(Map<String, dynamic> map) {
    return UserModel(
      firstName: map['firstName'] ?? '',
      lastName: map['lastName'] ?? '',
      phoneNumber: map['phoneNumber'] ?? '',
      email: map['email'] ?? '',
      cnic: map['cnic'] ?? '',
      district: map['district'] ?? '',
      gender: map['gender'] ?? '',
      designation: map['designation'] ?? '',
    );
  }
}
