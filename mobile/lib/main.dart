import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'providers/auth_provider.dart';
import 'providers/career_provider.dart';
import 'services/api_client.dart';
import 'services/auth_service.dart';
import 'services/career_service.dart';
import 'screens/splash_screen.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const EmbedHuntApp());
}

class EmbedHuntApp extends StatelessWidget {
  const EmbedHuntApp({super.key});

  @override
  Widget build(BuildContext context) {
    final api = ApiClient();
    final authService = AuthService(api);
    final careerService = CareerService(api);

    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider(authService)),
        ChangeNotifierProvider(create: (_) => CareerProvider(careerService)),
      ],
      child: MaterialApp(
        title: 'EMBEDHUNT AI',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.light,
        home: const SplashScreen(),
      ),
    );
  }
}
