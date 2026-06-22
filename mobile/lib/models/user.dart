/// Authenticated user, mirrors the API's `user` object.
class User {
  final String id;
  final String email;
  final String username;
  final String firstName;
  final String lastName;
  final String fullName;
  final String role;
  final bool isVerified;
  final bool isPremium;

  const User({
    required this.id,
    required this.email,
    required this.username,
    required this.firstName,
    required this.lastName,
    required this.fullName,
    required this.role,
    required this.isVerified,
    required this.isPremium,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String? ?? '',
      email: json['email'] as String? ?? '',
      username: json['username'] as String? ?? '',
      firstName: json['first_name'] as String? ?? '',
      lastName: json['last_name'] as String? ?? '',
      fullName: json['full_name'] as String? ?? '',
      role: json['role'] as String? ?? 'candidate',
      isVerified: json['is_verified'] as bool? ?? false,
      isPremium: json['is_premium'] as bool? ?? false,
    );
  }
}
