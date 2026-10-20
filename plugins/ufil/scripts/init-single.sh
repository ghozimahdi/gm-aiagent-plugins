#!/bin/bash
# UFIL — Scaffold single-module Flutter project
# Usage: ./init-single.sh <project_name> [package_name]
# Example: ./init-single.sh my_app com.example.myapp
# Default package_name: com.example.app
#
# Prerequisites: FVM must be installed (dart pub global activate fvm)
# Dependencies are fetched from pub.dev automatically (no hardcoded versions).

set -e

PROJECT_NAME="${1:?Usage: init-single.sh <project_name> [package_name]}"
PACKAGE_NAME="${2:-com.example.app}"
PROJECT_DIR="$(pwd)/$PROJECT_NAME"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/templates/single"

# ========================================
# PREREQUISITES
# ========================================
if ! command -v fvm &> /dev/null; then
  echo "❌ FVM is required. Install: dart pub global activate fvm"
  exit 1
fi

FVM_FLUTTER_VERSION=$(fvm flutter --version 2>/dev/null | head -1 | awk '{print $2}')
if [ -z "$FVM_FLUTTER_VERSION" ]; then
  echo "❌ Could not detect Flutter version from FVM. Run: fvm install <version> && fvm global <version>"
  exit 1
fi

DART_SDK_FULL=$(fvm dart --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
DART_SDK_MAJOR_MINOR=$(echo "$DART_SDK_FULL" | cut -d'.' -f1,2)
SDK_CONSTRAINT="^${DART_SDK_MAJOR_MINOR}.0"

echo "🏗️ Creating single-module Flutter project: $PROJECT_NAME ($PACKAGE_NAME)"
echo "   Flutter: $FVM_FLUTTER_VERSION | Dart SDK: $DART_SDK_FULL (constraint: $SDK_CONSTRAINT)"

# Helper: add deps using fvm dart pub add (always fetches latest from pub.dev)
pub_add() {
  fvm dart pub add "$@" 2>&1 | tail -1
}
pub_add_dev() {
  fvm dart pub add --dev "$@" 2>&1 | tail -1
}

# --- Create Flutter project ---
fvm flutter create "$PROJECT_NAME" --org "$PACKAGE_NAME" --empty
cd "$PROJECT_DIR"

# --- Update SDK constraint ---
if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' "s/sdk: .*/sdk: $SDK_CONSTRAINT/" pubspec.yaml
else
  sed -i "s/sdk: .*/sdk: $SDK_CONSTRAINT/" pubspec.yaml
fi

# --- analysis_options.yaml ---
cat > analysis_options.yaml << 'EOF'
include: package:lint/strict.yaml

analyzer:
  errors:
    always_declare_return_types: error
    missing_required_param: error
    missing_return: error
    must_be_immutable: error
    no_leading_underscores_for_local_identifiers: error
    prefer_const_constructors: error
    prefer_final_locals: ignore
    sort_unnamed_constructors_first: ignore
    use_is_even_rather_than_modulo: error
    avoid_empty_else: error
    invalid_annotation_target: ignore
    always_put_required_named_parameters_first: error
    avoid_print: error
    avoid_dynamic_calls: error
    avoid_types_on_closure_parameters: error
    cascade_invocations: error
    public_member_api_docs: error
    unawaited_futures: error
    prefer_expression_function_bodies: ignore
    require_trailing_commas: ignore
    sort_pub_dependencies: ignore

  exclude:
    - lib/**.freezed.dart
    - lib/**.g.dart
    - lib/**.gr.dart
    - lib/**.config.dart
    - lib/**.gen.dart

linter:
  rules:
    prefer_if_elements_to_conditional_expressions: false
EOF

# --- .fvmrc ---
cat > .fvmrc << EOF
{
  "flutter": "$FVM_FLUTTER_VERSION",
  "flavors": {}
}
EOF

# --- .gitignore (overwrite the one from `flutter create`) ---
cat > .gitignore << 'EOF'
# See https://www.dartlang.org/guides/libraries/private-files

# Files and directories created by pub
.dart_tool/
.packages
build/

# Avoid committing generated Javascript files:
*.dart.js
*.info.json
*.js
*.js_
*.js.deps
*.js.map

# Flutter/Dart related
.flutter-plugins
.flutter-plugins-dependencies

*.freezed.dart
*.config.dart
*.gr.dart
*.g.dart
*.gen.dart

# Miscellaneous
*.class
*.log
*.pyc
*.swp
.DS_Store
.atom/
.buildlog/
.history
.svn/

# IntelliJ related
*.iml
*.ipr
*.iws
.idea/

# Flutter/Dart/Pub related
.pub-cache/
.pub/

# Android related
**/android/**/gradle-wrapper.jar
**/android/.gradle
**/android/captures/
**/android/gradlew
**/android/gradlew.bat
**/android/local.properties
**/android/**/GeneratedPluginRegistrant.java

# iOS/XCode related
**/ios/**/*.mode{1v3,2v3}
**/ios/**/*.moved-aside
**/ios/**/*.pbxuser
**/ios/**/*.perspectivev3
**/ios/**/*sync/
**/ios/**/.sconsign.dblite
**/ios/**/.tags*
**/ios/**/.vagrant/
**/ios/**/DerivedData/
**/ios/**/Icon?
**/ios/**/Pods/
**/ios/**/.symlinks/
**/ios/**/profile
**/ios/**/xcuserdata
**/ios/.generated/
**/ios/Flutter/{App.framework, Flutter.framework, Generated.xcconfig, app.{flx,zip}, flutter_assets/}
**/ios/ServiceDefinitions.json
**/ios/Runner/GeneratedPluginRegistrant.*

# Exceptions to above rules.
!**/ios/**/default.{mode1v3, mode2v3, pbxuser, perspectivev3}
!/packages/flutter_tools/test/data/dart_dependencies_test/**/.packages
*.assets.dart

# .env files
.env
.env.local
.env_*
!.env.example

# Firebase configuration files
**/**/google-services.json
**/**/GoogleService-Info.plist
**/**/firebase_app_id_file.json

# Signing Key
*.jks

# Linux related (it's optional). This is temporary solution
**/linux/
generated
gen

# FVM Version Cache
.fvm/
devtools_options.yaml
EOF

# --- Core directories ---
mkdir -p lib/core/{config,error,network,local,result,router,theme,utils,widgets,extensions}
mkdir -p lib/gen
mkdir -p lib/l10n
mkdir -p lib/features/auth/domain/{models,repositories,usecases}
mkdir -p lib/features/auth/data/{models,mappers,datasources,repositories}
mkdir -p lib/features/auth/presentation/blocs/login
mkdir -p lib/features/auth/presentation/pages
mkdir -p lib/common/{domain/{repositories,usecases},data/datasources/local,presentation/blocs}
mkdir -p test/helpers
mkdir -p assets/{colors,icons,images}
mkdir -p releases

# ========================================
# WRITE ALL SOURCE FILES
# ========================================

# CORE — Result<T>
cat > lib/core/result/result.dart << EOF
import 'package:${PROJECT_NAME}/core/error/failures.dart';

sealed class Result<T> {
  const Result();
  const factory Result.ok(T value) = Ok<T>._;
  const factory Result.error(Failure error) = Error<T>._;
}

final class Ok<T> extends Result<T> {
  const Ok._(this.value);
  final T value;

  @override
  bool operator ==(Object other) {
    return other is Ok<T> && other.value == value;
  }

  @override
  int get hashCode {
    return value.hashCode;
  }
}

final class Error<T> extends Result<T> {
  const Error._(this.error);
  final Failure error;

  @override
  bool operator ==(Object other) {
    return other is Error<T> && other.error == error;
  }

  @override
  int get hashCode {
    return error.hashCode;
  }
}
EOF

cat > lib/core/result/paginated_response.dart << 'EOF'
class PaginatedResponse<T> {
  const PaginatedResponse({
    required this.data,
    required this.totalCount,
    required this.hasNextPage,
  });

  final List<T> data;
  final int totalCount;
  final bool hasNextPage;
}
EOF

# CORE — Error handling
cat > lib/core/error/failures.dart << 'DART'
import 'package:freezed_annotation/freezed_annotation.dart';

part 'failures.freezed.dart';

/// Base failure class for representing errors in the domain layer.
@freezed
sealed class Failure with _$Failure {
  const Failure._();

  const factory Failure.server({
    @Default('Server error occurred') String message,
    int? statusCode,
  }) = ServerFailure;

  const factory Failure.network([
    @Default('No internet connection') String message,
  ]) = NetworkFailure;

  const factory Failure.cache([
    @Default('Cache error occurred') String message,
  ]) = CacheFailure;

  const factory Failure.validation({
    @Default('Validation failed') String message,
    Map<String, List<String>>? errors,
  }) = ValidationFailure;

  const factory Failure.auth([
    @Default('Authentication failed') String message,
  ]) = AuthFailure;

  const factory Failure.rateLimit({
    @Default('Too many requests') String message,
    int? retryAfterSeconds,
  }) = RateLimitFailure;

  const factory Failure.unexpected([
    @Default('Unexpected error') String message,
  ]) = UnexpectedFailure;

  const factory Failure.noFailure({@Default('No failure') String message}) =
      NoFailure;
}
DART

cat > lib/core/error/exceptions.dart << 'EOF'
/// Base exception class for all custom exceptions.
sealed class AppException implements Exception {
  const AppException([this.message]);

  final String? message;

  @override
  String toString() {
    return message ?? 'AppException';
  }
}

/// Exception thrown when a server error occurs.
class ServerException extends AppException {
  const ServerException({String? message, this.statusCode}) : super(message);

  final int? statusCode;
}

/// Exception thrown when a network error occurs.
class NetworkException extends AppException {
  const NetworkException([super.message]);
}

/// Exception thrown when a cache error occurs.
class CacheException extends AppException {
  const CacheException([super.message]);
}

/// Exception thrown when validation fails.
class ValidationException extends AppException {
  const ValidationException({String? message, this.errors}) : super(message);

  final Map<String, List<String>>? errors;
}

/// Exception thrown when authentication fails.
class UnauthorizedException extends AppException {
  const UnauthorizedException([super.message]);
}

/// Exception thrown when rate limit is exceeded.
class RateLimitException extends AppException {
  const RateLimitException({String? message, this.retryAfterSeconds})
    : super(message);

  final int? retryAfterSeconds;
}

/// Exception thrown when access is forbidden.
class ForbiddenException extends AppException {
  const ForbiddenException([super.message]);
}

/// Exception thrown for general client errors (4xx).
class ClientException extends AppException {
  const ClientException({String? message, this.statusCode}) : super(message);

  final int? statusCode;
}
EOF

# CORE — Error type enum
cat > lib/core/error/error_type.dart << 'EOF'
/// Types of application errors for UI categorization.
enum ErrorType {
  /// Validation error (e.g., invalid input format).
  validation,

  /// Rate limit exceeded.
  rateLimit,

  /// Authentication error.
  auth,

  /// Network connectivity error.
  network,

  /// Server error.
  server,

  /// Unknown or unexpected error.
  unknown,
}
EOF

# CORE — Exception → Failure mapper
cat > lib/core/error/exception_mapper.dart << EOF
import 'package:${PROJECT_NAME}/core/error/exceptions.dart';
import 'package:${PROJECT_NAME}/core/error/failures.dart';

/// Extension on [AppException] to convert exceptions to failures.
extension ExceptionMapper on AppException {
  /// Converts this [AppException] to its corresponding [Failure].
  Failure toFailure() {
    return switch (this) {
      ValidationException(:final message, :final errors) => ValidationFailure(
        message: message ?? 'Validation failed',
        errors: errors,
      ),
      RateLimitException(:final message, :final retryAfterSeconds) =>
        RateLimitFailure(
          message: message ?? 'Too many requests',
          retryAfterSeconds: retryAfterSeconds,
        ),
      UnauthorizedException(:final message) => AuthFailure(
        message ?? 'Authentication failed',
      ),
      NetworkException(:final message) => NetworkFailure(
        message ?? 'No internet connection',
      ),
      ServerException(:final message, :final statusCode) => ServerFailure(
        message: message ?? 'Server error',
        statusCode: statusCode,
      ),
      CacheException(:final message) => CacheFailure(message ?? 'Cache error'),
      ForbiddenException(:final message) => ServerFailure(
        message: message ?? 'Access denied',
      ),
      ClientException(:final message, :final statusCode) => ServerFailure(
        message: message ?? 'Client error',
        statusCode: statusCode,
      ),
    };
  }
}
EOF

# CORE — Failure → ErrorType + display message
cat > lib/core/error/failure_mapper.dart << EOF
import 'package:${PROJECT_NAME}/core/error/error_type.dart';
import 'package:${PROJECT_NAME}/core/error/failures.dart';

/// Extension on [Failure] to provide default error messages and error types.
extension FailureMapper on Failure {
  /// Returns the appropriate [ErrorType] for this failure.
  ErrorType get errorType {
    return switch (this) {
      ValidationFailure() => ErrorType.validation,
      RateLimitFailure() => ErrorType.rateLimit,
      AuthFailure() => ErrorType.auth,
      NetworkFailure() => ErrorType.network,
      ServerFailure() => ErrorType.server,
      CacheFailure() => ErrorType.server,
      UnexpectedFailure() => ErrorType.unknown,
      NoFailure() => ErrorType.unknown,
    };
  }

  /// Returns the error message, or a default message if not provided.
  String get displayMessage {
    if (message.isNotEmpty) {
      return message;
    }
    return defaultMessage;
  }

  /// Returns the default message for this failure type.
  String get defaultMessage {
    return switch (this) {
      ValidationFailure() => 'Validation failed',
      RateLimitFailure() => 'Too many requests. Please wait.',
      AuthFailure() => 'Authentication failed',
      NetworkFailure() => 'Network error. Please check your connection.',
      ServerFailure() => 'Server error. Please try again.',
      CacheFailure() => 'Cache error occurred',
      UnexpectedFailure() => 'An unexpected error occurred',
      NoFailure() => 'No failure occurred',
    };
  }
}
EOF

cat > lib/core/error/error_mapper.dart << EOF
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:${PROJECT_NAME}/core/error/exception_mapper.dart';
import 'package:${PROJECT_NAME}/core/error/exceptions.dart';
import 'package:${PROJECT_NAME}/core/error/failures.dart';

/// Mixin that provides error mapping functionality for repositories.
///
/// Example:
/// \`\`\`dart
/// class MyRepositoryImpl with ErrorMapper implements MyRepository {
///   @override
///   Future<Result<Data>> fetchData() async {
///     try {
///       final data = await dataSource.fetchData();
///       return Result.ok(data);
///     } catch (e) {
///       return Result.error(mapToFailure(e));
///     }
///   }
/// }
/// \`\`\`
mixin ErrorMapper {
  /// Maps any error to a [Failure].
  Failure mapToFailure(Object error) {
    if (kDebugMode) {
      debugPrint('Mapping error: \$error');
    }

    if (error is AppException) {
      return error.toFailure();
    }

    if (error is DioException) {
      return _mapDioException(error);
    }

    return Failure.unexpected('Unexpected error: \$error');
  }

  Failure _mapDioException(DioException exception) {
    final wrappedError = exception.error;
    if (wrappedError is AppException) {
      return wrappedError.toFailure();
    }

    return switch (exception.type) {
      DioExceptionType.connectionTimeout ||
      DioExceptionType.sendTimeout ||
      DioExceptionType.receiveTimeout => const Failure.network(
        'Connection timed out',
      ),
      DioExceptionType.connectionError => const Failure.network(),
      DioExceptionType.badCertificate => const Failure.network(
        'SSL certificate error',
      ),
      _ => Failure.network(exception.message ?? 'Network error occurred'),
    };
  }
}
EOF

# CORE — Network
cat > lib/core/network/network_module.dart << EOF
import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart';
import 'package:${PROJECT_NAME}/core/config/env.dart';
import 'package:${PROJECT_NAME}/core/network/dio_error_interceptor.dart';

@module
abstract class NetworkModule {
  @lazySingleton
  Dio dio(Env env) {
    final dio = Dio(
      BaseOptions(
        baseUrl: env.apiBaseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 30),
        contentType: 'application/json',
      ),
    );
    dio.interceptors.add(DioErrorInterceptor());
    return dio;
  }
}
EOF

cat > lib/core/network/dio_error_interceptor.dart << EOF
import 'package:dio/dio.dart';
import 'package:${PROJECT_NAME}/core/error/exceptions.dart';

/// Translates [DioException] into [AppException] subclasses.
class DioErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    switch (err.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        throw const NetworkException('Connection timed out');
      case DioExceptionType.connectionError:
        throw const NetworkException('No internet connection');
      case DioExceptionType.badResponse:
        final statusCode = err.response?.statusCode ?? 0;
        if (statusCode == 401) {
          throw const UnauthorizedException('Unauthorized');
        } else if (statusCode == 403) {
          throw const ForbiddenException('Access denied');
        } else if (statusCode == 429) {
          throw const RateLimitException(message: 'Too many requests');
        } else if (statusCode >= 500) {
          throw ServerException(
            message: 'Server error: \$statusCode',
            statusCode: statusCode,
          );
        } else {
          throw ClientException(
            message: 'Request failed: \$statusCode',
            statusCode: statusCode,
          );
        }
      default:
        throw ServerException(message: 'Unexpected error: \${err.message}');
    }
  }
}
EOF

# CORE — Local storage
cat > lib/core/local/local_module.dart << 'DART'
import 'package:encrypt_shared_preferences/provider.dart';
import 'package:injectable/injectable.dart';

@module
abstract class LocalModule {
  @lazySingleton
  EncryptedSharedPreferences get encryptedPrefs {
    return EncryptedSharedPreferences.getInstance();
  }
}
DART

# CORE — Config
cat > lib/core/config/env.dart << 'DART'
import 'package:envied/envied.dart';
import 'package:injectable/injectable.dart';

part 'env.g.dart';

@Envied(path: '.env', obfuscate: true, useConstantCase: true)
@singleton
class Env {
  @EnviedField(defaultValue: '')
  final String apiBaseUrl = _Env.apiBaseUrl;
}
DART

# GEN — Colors (FlutterGen-style; replace with real generated file when adding flutter_gen)
cat > lib/gen/colors.gen.dart << 'EOF'
// dart format width=80
/// GENERATED CODE - DO NOT MODIFY BY HAND
/// *****************************************************
///  FlutterGen
/// *****************************************************

// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: deprecated_member_use,directives_ordering,implicit_dynamic_list_literal,unnecessary_import

import 'package:flutter/painting.dart';

class AppColors {
  AppColors._();

  /// Color: #121212
  static const Color backgroundDark = Color(0xFF121212);

  /// Color: #FFFFFF
  static const Color backgroundLight = Color(0xFFFFFFFF);

  /// Color: #D32F2F
  static const Color error = Color(0xFFD32F2F);

  /// Color: #1A73E8
  static const Color primary = Color(0xFF1A73E8);

  /// Color: #1557B0
  static const Color primaryDark = Color(0xFF1557B0);

  /// Color: #1E1E1E
  static const Color surfaceDark = Color(0xFF1E1E1E);

  /// Color: #FFFFFF
  static const Color textPrimaryDark = Color(0xFFFFFFFF);

  /// Color: #1A1A1A
  static const Color textPrimaryLight = Color(0xFF1A1A1A);

  /// Color: #AAAAAA
  static const Color textSecondaryDark = Color(0xFFAAAAAA);

  /// Color: #757575
  static const Color textSecondaryLight = Color(0xFF757575);
}
EOF

# CORE — Theme
cat > lib/core/theme/app_theme.dart << EOF
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:${PROJECT_NAME}/gen/colors.gen.dart';

class AppTheme {
  const AppTheme._();

  static ThemeData get lightTheme {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: AppColors.primary,
      surface: AppColors.backgroundLight,
      error: AppColors.error,
      primary: AppColors.primaryDark,
    );
    final primary = colorScheme.primary;

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: AppColors.backgroundLight,
      appBarTheme: const AppBarTheme(
        elevation: 0,
        backgroundColor: AppColors.backgroundLight,
        foregroundColor: AppColors.textPrimaryLight,
        centerTitle: false,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primary,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12.r),
          ),
          padding: EdgeInsets.symmetric(vertical: 14.h, horizontal: 24.w),
        ),
      ),
      cardTheme: CardThemeData(
        color: Colors.white,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12.r),
          side: BorderSide(color: Colors.grey.shade300),
        ),
      ),
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: primary,
        foregroundColor: Colors.white,
      ),
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        selectedItemColor: primary,
        unselectedItemColor: Colors.grey,
        backgroundColor: Colors.white,
      ),
      bottomSheetTheme: const BottomSheetThemeData(
        backgroundColor: Colors.white,
      ),
      chipTheme: ChipThemeData(
        showCheckmark: true,
        checkmarkColor: AppColors.backgroundLight,
        selectedColor: primary,
        backgroundColor: Colors.transparent,
        side: WidgetStateBorderSide.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return const BorderSide(color: Colors.transparent, width: 1.5);
          }
          return BorderSide(color: Colors.grey.shade300);
        }),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20.r),
        ),
        labelStyle: const TextStyle(color: AppColors.textPrimaryLight),
        secondaryLabelStyle: const TextStyle(color: AppColors.textPrimaryDark),
      ),
    );
  }

  static ThemeData get darkTheme {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: AppColors.primary,
      brightness: Brightness.dark,
      surface: AppColors.surfaceDark,
      error: AppColors.error,
    );
    final primary = colorScheme.primary;

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: AppColors.backgroundDark,
      appBarTheme: const AppBarTheme(
        elevation: 0,
        backgroundColor: AppColors.backgroundDark,
        foregroundColor: AppColors.textPrimaryDark,
        centerTitle: false,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12.r),
          ),
          padding: EdgeInsets.symmetric(vertical: 14.h, horizontal: 24.w),
        ),
      ),
      cardTheme: CardThemeData(
        color: AppColors.surfaceDark,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12.r),
          side: BorderSide(color: Colors.grey.shade700),
        ),
      ),
      chipTheme: ChipThemeData(
        showCheckmark: true,
        checkmarkColor: primary,
        selectedColor: AppColors.surfaceDark,
        backgroundColor: Colors.transparent,
        side: WidgetStateBorderSide.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return BorderSide(color: primary, width: 1.5);
          }
          return BorderSide(color: Colors.grey.shade700);
        }),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20.r),
        ),
        labelStyle: const TextStyle(color: AppColors.textPrimaryDark),
        secondaryLabelStyle: TextStyle(color: primary),
      ),
    );
  }
}
EOF

# CORE — Utils
cat > lib/core/utils/bloc_transformer_mixin.dart << 'EOF'
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:rxdart/rxdart.dart';

/// Reusable Bloc event transformers (debounce + switchMap) backed by RxDart.
mixin BlocTransformerMixin {
  /// Debounces events for 300ms then maps the latest one, cancelling prior work.
  EventTransformer<T> debounceTransformer<T>() {
    return (events, mapper) {
      return events
          .debounceTime(const Duration(milliseconds: 300))
          .switchMap(mapper);
    };
  }
}
EOF

# CORE — Extensions
cat > lib/core/extensions/build_context_extensions.dart << EOF
import 'package:flutter/material.dart';
import 'package:${PROJECT_NAME}/gen/l10n/app_localizations.dart';

/// Convenient access to localized strings via \`context.l10n\`.
extension BuildContextL10n on BuildContext {
  /// Returns the [AppLocalizations] for the current [BuildContext].
  AppLocalizations get l10n {
    return AppLocalizations.of(this)!;
  }
}
EOF

# CORE — Nullable extensions (mapper/repo/use-case helpers; canonical, do NOT duplicate)
cat > lib/core/extensions/nullable_extensions.dart << 'EOF'
extension StringExtensions on String? {
  String orEmpty() => this ?? '';
}

extension ListExtensions<T> on List<T>? {
  List<T> orEmpty() => this ?? [];
}

extension IntExtensions on int? {
  int orZero() => this ?? 0;
}

extension DoubleExtensions on double? {
  double orZero() => this ?? 0.0;
}

extension BoolExtensions on bool? {
  bool orFalse() => this ?? false;
  bool? orNull() => this == false ? null : this;
}

extension StringOrNullExtensions on String {
  String? orNull() => isNotEmpty ? this : null;
}

extension ListOrNullExtensions<T> on List<T> {
  List<T>? orNull() => isNotEmpty ? this : null;
}

extension IntOrNullExtensions on int {
  int? orNull() => this == 0 ? null : this;
}

extension DoubleOrNullExtensions on double {
  double? orNull() => this == 0 ? null : this;
}

extension DateTimeOrNullExtensions on DateTime? {
  /// ISO-8601 calendar date `yyyy-MM-dd`, or null when receiver is null.
  /// Use in Request mappers to send a date string or omit the field.
  String? toIsoDate() {
    final value = this;
    if (value == null) {
      return null;
    }
    final yyyy = value.year.toString().padLeft(4, '0');
    final mm = value.month.toString().padLeft(2, '0');
    final dd = value.day.toString().padLeft(2, '0');
    return '$yyyy-$mm-$dd';
  }
}
EOF

# CORE — Dash extensions (UI/display only; "-" fallback; NEVER inside a mapper)
cat > lib/core/extensions/dash_extensions.dart << 'EOF'
extension StringDashExtensions on String? {
  /// Returns "-" when receiver is null or trimmed-empty, otherwise the trimmed value.
  /// Use in UI/display only. NEVER inside a mapper or repository.
  String orDash() {
    final value = this;
    if (value == null) {
      return '-';
    }
    final trimmed = value.trim();
    if (trimmed.isEmpty) {
      return '-';
    }
    return trimmed;
  }
}

extension IntDashExtensions on int? {
  /// Returns "-" when receiver is null or `0`, otherwise `toString()`.
  String orDash() {
    final value = this;
    if (value == null || value == 0) {
      return '-';
    }
    return value.toString();
  }
}

extension DoubleDashExtensions on double? {
  /// Returns "-" when receiver is null or `0`, otherwise `toString()`.
  String orDash() {
    final value = this;
    if (value == null || value == 0) {
      return '-';
    }
    return value.toString();
  }
}

extension DateTimeDashExtensions on DateTime? {
  /// Returns "-" when receiver is null, otherwise the ISO calendar date `yyyy-MM-dd`.
  /// For human-facing dates, prefer a localized formatter (e.g. `DateFormat.yMMMd()`).
  String orDash() {
    final value = this;
    if (value == null) {
      return '-';
    }
    final yyyy = value.year.toString().padLeft(4, '0');
    final mm = value.month.toString().padLeft(2, '0');
    final dd = value.day.toString().padLeft(2, '0');
    return '$yyyy-$mm-$dd';
  }
}
EOF

# L10N — Configuration
cat > l10n.yaml << 'EOF'
arb-dir: lib/l10n
template-arb-file: app_en.arb
output-localization-file: app_localizations.dart
output-class: AppLocalizations
output-dir: lib/gen/l10n
EOF

cat > lib/l10n/app_en.arb << 'EOF'
{
  "@@locale": "en",
  "appName": "My App",
  "login": "Login",
  "logout": "Logout",
  "email": "Email",
  "password": "Password",
  "signIn": "Sign In",
  "loading": "Loading...",
  "errorOccurred": "An error occurred",
  "validationEmailRequired": "Email is required",
  "validationPasswordRequired": "Password is required"
}
EOF

cat > lib/l10n/app_id.arb << 'EOF'
{
  "@@locale": "id",
  "appName": "Aplikasi Saya",
  "login": "Masuk",
  "logout": "Keluar",
  "email": "Email",
  "password": "Kata Sandi",
  "signIn": "Masuk",
  "loading": "Memuat...",
  "errorOccurred": "Terjadi kesalahan",
  "validationEmailRequired": "Email wajib diisi",
  "validationPasswordRequired": "Kata sandi wajib diisi"
}
EOF

# ========================================
# FEATURE — Auth (best-practice scaffold demonstrating ALL conventions)
# ========================================
# Structure demonstrated here:
#   Domain:
#     models/user_model.dart           — @freezed Model with @Default
#     models/login_params.dart          — @freezed Params (≥4 fields rule isn't met but shown for example)
#     models/login_result.dart         — @freezed Result (no Failure — Result<T> wraps it)
#     repositories/auth_repository.dart — abstract, returns Future<Result<T>>
#     usecases/login_use_case.dart     — @lazySingleton, plain call()
#   Data:
#     models/user_dto.dart             — @freezed DTO + @JsonKey + fromJson, NO .toModel()
#     models/login_request.dart        — @freezed Request + toJson
#     models/login_response.dart       — @freezed Response + fromJson
#     mappers/user_model_mapper.dart   — @lazySingleton, mapFromData(UserDto?)
#     mappers/login_result_mapper.dart — @lazySingleton, mapFromData(LoginResponse?)
#     mappers/login_request_mapper.dart — @lazySingleton, mapFromDomain(LoginParams)
#     datasources/auth_remote_data_source.dart — @lazySingleton, returns Response/DTO, NO try/catch
#     repositories/auth_repository_impl.dart — with ErrorMapper, injects mappers + datasource
#   Presentation:
#     blocs/login/login_bloc.dart      — sub-state union per async action, init event, switch on Result
#     blocs/login/login_event.dart     — @freezed abstract class, _InitEvent + _SubmittedEvent
#     blocs/login/login_state.dart     — main state + SubmitLoginState (idle/loading/done/error) + AlertState
#     pages/login_page.dart            — @RoutePage, BlocProvider with init event dispatch

# DOMAIN — UserModel
cat > lib/features/auth/domain/models/user_model.dart << 'DART'
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user_model.freezed.dart';

@freezed
abstract class UserModel with _$UserModel {
  const factory UserModel({
    @Default('') String id,
    @Default('') String name,
    @Default('') String email,
  }) = _UserModel;
}
DART

# DOMAIN — LoginParams
cat > lib/features/auth/domain/models/login_params.dart << 'DART'
import 'package:freezed_annotation/freezed_annotation.dart';

part 'login_params.freezed.dart';

/// Domain Params for login.
///
/// Per DOMAIN_LAYER.md: Params class is normally only created when ≥4 fields.
/// Login has 2 fields, but we use a class here to demonstrate the
/// Params → Request mapper pattern for the scaffold.
@freezed
abstract class LoginParams with _$LoginParams {
  const factory LoginParams({
    @Default('') String email,
    @Default('') String password,
  }) = _LoginParams;
}
DART

# DOMAIN — LoginResult (no Failure — Result<T> wraps it in single-module)
cat > lib/features/auth/domain/models/login_result.dart << 'DART'
import 'package:freezed_annotation/freezed_annotation.dart';

import 'user_model.dart';

part 'login_result.freezed.dart';

/// Result for login. Carries the auth token + user.
///
/// Single-module Results do NOT carry `Failure`; `Result<T>` from the repo
/// wraps the failure. This keeps Result free of error concerns and matches
/// the `state.submitState.result` ergonomics in the bloc.
@freezed
abstract class LoginResult with _$LoginResult {
  const factory LoginResult({
    @Default('') String token,
    @Default(UserModel()) UserModel user,
  }) = _LoginResult;
}
DART

# DOMAIN — Repository contract
cat > lib/features/auth/domain/repositories/auth_repository.dart << EOF
import 'package:${PROJECT_NAME}/core/result/result.dart';
import 'package:${PROJECT_NAME}/features/auth/domain/models/login_params.dart';
import 'package:${PROJECT_NAME}/features/auth/domain/models/login_result.dart';

/// Contract for authentication operations.
abstract class AuthRepository {
  /// Logs the user in and returns the auth token + user wrapped in [Result].
  Future<Result<LoginResult>> login(LoginParams params);

  /// Logs the current user out.
  Future<Result<void>> logout();
}
EOF

# DOMAIN — UseCase (note: UseCase suffix, file name uses _use_case.dart)
cat > lib/features/auth/domain/usecases/login_use_case.dart << EOF
import 'package:injectable/injectable.dart';
import 'package:${PROJECT_NAME}/core/result/result.dart';
import 'package:${PROJECT_NAME}/features/auth/domain/models/login_params.dart';
import 'package:${PROJECT_NAME}/features/auth/domain/models/login_result.dart';
import 'package:${PROJECT_NAME}/features/auth/domain/repositories/auth_repository.dart';

/// Use case that logs the user in.
@lazySingleton
class LoginUseCase {
  LoginUseCase(this._repository);

  final AuthRepository _repository;

  Future<Result<LoginResult>> call(LoginParams params) {
    return _repository.login(params);
  }
}
EOF

cat > lib/features/auth/domain/usecases/logout_use_case.dart << EOF
import 'package:injectable/injectable.dart';
import 'package:${PROJECT_NAME}/core/result/result.dart';
import 'package:${PROJECT_NAME}/features/auth/domain/repositories/auth_repository.dart';

/// Use case that logs the current user out.
@lazySingleton
class LogoutUseCase {
  LogoutUseCase(this._repository);

  final AuthRepository _repository;

  Future<Result<void>> call() {
    return _repository.logout();
  }
}
EOF

# DATA — UserDto
cat > lib/features/auth/data/models/user_dto.dart << 'DART'
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user_dto.freezed.dart';
part 'user_dto.g.dart';

/// Wire format for User. All fields nullable + @JsonKey on EVERY field.
/// NO .toModel() — mapping lives in UserModelMapper (separate class).
@freezed
abstract class UserDto with _$UserDto {
  const factory UserDto({
    @JsonKey(name: 'id') String? id,
    @JsonKey(name: 'name') String? name,
    @JsonKey(name: 'email') String? email,
  }) = _UserDto;

  factory UserDto.fromJson(Map<String, dynamic> json) {
    return _$UserDtoFromJson(json);
  }
}
DART

# DATA — LoginResponse
cat > lib/features/auth/data/models/login_response.dart << 'DART'
import 'package:freezed_annotation/freezed_annotation.dart';

import 'user_dto.dart';

part 'login_response.freezed.dart';
part 'login_response.g.dart';

/// Full API response for /auth/login.
@freezed
abstract class LoginResponse with _$LoginResponse {
  const factory LoginResponse({
    @JsonKey(name: 'token') String? token,
    @JsonKey(name: 'user') UserDto? user,
  }) = _LoginResponse;

  factory LoginResponse.fromJson(Map<String, dynamic> json) {
    return _$LoginResponseFromJson(json);
  }
}
DART

# DATA — LoginRequest (toJson generated by json_serializable)
cat > lib/features/auth/data/models/login_request.dart << 'DART'
import 'package:freezed_annotation/freezed_annotation.dart';

part 'login_request.freezed.dart';
part 'login_request.g.dart';

/// Outgoing request body for POST /auth/login.
@freezed
abstract class LoginRequest with _$LoginRequest {
  const factory LoginRequest({
    @JsonKey(name: 'email') required String email,
    @JsonKey(name: 'password') required String password,
  }) = _LoginRequest;

  factory LoginRequest.fromJson(Map<String, dynamic> json) {
    return _$LoginRequestFromJson(json);
  }
}
DART

# DATA — UserModelMapper (separate @lazySingleton class)
cat > lib/features/auth/data/mappers/user_model_mapper.dart << EOF
import 'package:injectable/injectable.dart';
import 'package:${PROJECT_NAME}/features/auth/data/models/user_dto.dart';
import 'package:${PROJECT_NAME}/features/auth/domain/models/user_model.dart';

/// Maps [UserDto] → [UserModel] with safe defaults.
@lazySingleton
class UserModelMapper {
  UserModel mapFromData(UserDto? data) {
    return UserModel(
      id: data?.id ?? '',
      name: data?.name ?? '',
      email: data?.email ?? '',
    );
  }
}
EOF

# DATA — LoginResultMapper (composes UserModelMapper)
cat > lib/features/auth/data/mappers/login_result_mapper.dart << EOF
import 'package:injectable/injectable.dart';
import 'package:${PROJECT_NAME}/features/auth/data/mappers/user_model_mapper.dart';
import 'package:${PROJECT_NAME}/features/auth/data/models/login_response.dart';
import 'package:${PROJECT_NAME}/features/auth/domain/models/login_result.dart';

/// Maps [LoginResponse] → [LoginResult].
@lazySingleton
class LoginResultMapper {
  LoginResultMapper(this._userModelMapper);

  final UserModelMapper _userModelMapper;

  LoginResult mapFromData(LoginResponse? data) {
    return LoginResult(
      token: data?.token ?? '',
      user: _userModelMapper.mapFromData(data?.user),
    );
  }
}
EOF

# DATA — LoginRequestMapper (Params → Request)
cat > lib/features/auth/data/mappers/login_request_mapper.dart << EOF
import 'package:injectable/injectable.dart';
import 'package:${PROJECT_NAME}/features/auth/data/models/login_request.dart';
import 'package:${PROJECT_NAME}/features/auth/domain/models/login_params.dart';

/// Maps [LoginParams] → [LoginRequest].
@lazySingleton
class LoginRequestMapper {
  LoginRequest mapFromDomain(LoginParams params) {
    return LoginRequest(email: params.email, password: params.password);
  }
}
EOF

# DATA — Remote data source (returns Response/DTO, NO try/catch)
cat > lib/features/auth/data/datasources/auth_remote_data_source.dart << EOF
import 'package:dio/dio.dart';
import 'package:injectable/injectable.dart';
import 'package:${PROJECT_NAME}/features/auth/data/models/login_request.dart';
import 'package:${PROJECT_NAME}/features/auth/data/models/login_response.dart';
import 'package:${PROJECT_NAME}/features/auth/data/models/user_dto.dart';

/// Remote data source for authentication.
///
/// This scaffold ships with a dummy in-memory implementation so the app runs
/// out-of-the-box. Replace [login] and [logout] with real Dio calls — the Dio
/// instance is already wired up via NetworkModule:
///
/// \`\`\`dart
/// final response = await _dio.post('/auth/login', data: request.toJson());
/// return LoginResponse.fromJson(response.data as Map<String, dynamic>);
/// \`\`\`
@lazySingleton
class AuthRemoteDataSource {
  AuthRemoteDataSource(this._dio);

  // ignore: unused_field
  final Dio _dio;

  Future<LoginResponse> login(LoginRequest request) async {
    await Future<void>.delayed(const Duration(milliseconds: 800));
    if (request.email == 'demo@example.com' && request.password == 'password') {
      return const LoginResponse(
        token: 'put your token here',
        user: UserDto(id: '1', name: 'Demo User', email: 'demo@example.com'),
      );
    }
    throw Exception('Invalid credentials');
  }

  Future<void> logout() async {
    await Future<void>.delayed(const Duration(milliseconds: 200));
  }
}
EOF

# DATA — Repository impl (with ErrorMapper, injects mappers + datasource)
cat > lib/features/auth/data/repositories/auth_repository_impl.dart << EOF
import 'package:injectable/injectable.dart';
import 'package:${PROJECT_NAME}/core/error/error_mapper.dart';
import 'package:${PROJECT_NAME}/core/result/result.dart';
import 'package:${PROJECT_NAME}/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:${PROJECT_NAME}/features/auth/data/mappers/login_result_mapper.dart';
import 'package:${PROJECT_NAME}/features/auth/data/mappers/login_request_mapper.dart';
import 'package:${PROJECT_NAME}/features/auth/domain/models/login_params.dart';
import 'package:${PROJECT_NAME}/features/auth/domain/models/login_result.dart';
import 'package:${PROJECT_NAME}/features/auth/domain/repositories/auth_repository.dart';

@LazySingleton(as: AuthRepository)
class AuthRepositoryImpl with ErrorMapper implements AuthRepository {
  AuthRepositoryImpl(
    this._dataSource,
    this._loginRequestMapper,
    this._loginResultMapper,
  );

  final AuthRemoteDataSource _dataSource;
  final LoginRequestMapper _loginRequestMapper;
  final LoginResultMapper _loginResultMapper;

  @override
  Future<Result<LoginResult>> login(LoginParams params) async {
    try {
      final request = _loginRequestMapper.mapFromDomain(params);
      final response = await _dataSource.login(request);
      return Result.ok(_loginResultMapper.mapFromData(response));
    } catch (e) {
      return Result.error(mapToFailure(e));
    }
  }

  @override
  Future<Result<void>> logout() async {
    try {
      await _dataSource.logout();
      return const Result.ok(null);
    } catch (e) {
      return Result.error(mapToFailure(e));
    }
  }
}
EOF

# PRESENTATION — Login event (init mandatory + submitted)
cat > lib/features/auth/presentation/blocs/login/login_event.dart << 'DART'
part of 'login_bloc.dart';

@freezed
abstract class LoginEvent with _$LoginEvent {
  const factory LoginEvent.init({
    @Default(LoginState()) LoginState state,
  }) = _InitEvent;

  const factory LoginEvent.submitted({
    required String email,
    required String password,
  }) = _SubmittedEvent;
}
DART

# PRESENTATION — Login state (sub-state union per async action + AlertState)
cat > lib/features/auth/presentation/blocs/login/login_state.dart << 'DART'
part of 'login_bloc.dart';

/// Main state. Each async action gets its own sub-state class.
@freezed
abstract class LoginState with _$LoginState {
  const factory LoginState({
    @Default(SubmitLoginState.idle()) SubmitLoginState submitState,
    @Default(AlertState.idle()) AlertState alertState,
  }) = _LoginState;
}

/// Sub-state for the login submission. Uniform shape across all 4 variants:
/// every variant carries `result` and `failure` so consumers can read the
/// last successful payload OR the failure regardless of which variant is
/// active.
@freezed
abstract class SubmitLoginState with _$SubmitLoginState {
  const factory SubmitLoginState.idle({
    @Default(LoginResult()) LoginResult result,
    @Default(Failure.noFailure()) Failure failure,
  }) = _SubmitLoginIdleState;

  const factory SubmitLoginState.loading({
    @Default(LoginResult()) LoginResult result,
    @Default(Failure.noFailure()) Failure failure,
  }) = SubmitLoginLoadingState;

  const factory SubmitLoginState.done({
    @Default(LoginResult()) LoginResult result,
    @Default(Failure.noFailure()) Failure failure,
  }) = SubmitLoginDoneState;

  const factory SubmitLoginState.error({
    @Default(LoginResult()) LoginResult result,
    @Default(Failure.noFailure()) Failure failure,
  }) = SubmitLoginErrorState;
}

/// Generic alert flag — UI listens to this for snackbars / dialogs.
@freezed
abstract class AlertState with _$AlertState {
  const factory AlertState.idle() = _AlertIdleState;
  const factory AlertState.error() = AlertErrorState;
  const factory AlertState.done() = AlertDoneState;
}
DART

# PRESENTATION — Login bloc (switch on Result<LoginResult>)
cat > lib/features/auth/presentation/blocs/login/login_bloc.dart << EOF
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:injectable/injectable.dart';
import 'package:${PROJECT_NAME}/core/error/failures.dart';
import 'package:${PROJECT_NAME}/core/result/result.dart';
import 'package:${PROJECT_NAME}/features/auth/domain/models/login_params.dart';
import 'package:${PROJECT_NAME}/features/auth/domain/models/login_result.dart';
import 'package:${PROJECT_NAME}/features/auth/domain/usecases/login_use_case.dart';

part 'login_bloc.freezed.dart';
part 'login_event.dart';
part 'login_state.dart';

@injectable
class LoginBloc extends Bloc<LoginEvent, LoginState> {
  LoginBloc(this._loginUseCase) : super(const LoginState()) {
    on<_InitEvent>(_initEvent);
    on<_SubmittedEvent>(_submittedEvent);
  }

  final LoginUseCase _loginUseCase;

  Future<void> _initEvent(_InitEvent event, Emitter<LoginState> emit) async {
    emit(event.state);
  }

  Future<void> _submittedEvent(
    _SubmittedEvent event,
    Emitter<LoginState> emit,
  ) async {
    emit(
      state.copyWith(
        submitState: const SubmitLoginState.loading(),
        alertState: const AlertState.idle(),
      ),
    );

    final params = LoginParams(email: event.email, password: event.password);
    final result = await _loginUseCase(params);

    switch (result) {
      case Ok(:final value):
        emit(
          state.copyWith(
            submitState: SubmitLoginState.done(result: value),
            alertState: const AlertState.done(),
          ),
        );
      case Error(:final error):
        emit(
          state.copyWith(
            submitState: SubmitLoginState.error(failure: error),
            alertState: const AlertState.error(),
          ),
        );
    }
  }
}
EOF

# PRESENTATION — Login page (BlocProvider dispatches init event)
cat > lib/features/auth/presentation/pages/login_page.dart << EOF
import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:${PROJECT_NAME}/core/error/failure_mapper.dart';
import 'package:${PROJECT_NAME}/core/extensions/build_context_extensions.dart';
import 'package:${PROJECT_NAME}/features/auth/presentation/blocs/login/login_bloc.dart';
import 'package:${PROJECT_NAME}/injector.dart';

@RoutePage()
class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => getIt<LoginBloc>()..add(const LoginEvent.init()),
      child: const _LoginView(),
    );
  }
}

class _LoginView extends StatefulWidget {
  const _LoginView();

  @override
  State<_LoginView> createState() => _LoginViewState();
}

class _LoginViewState extends State<_LoginView> {
  final _emailController = TextEditingController(text: 'demo@example.com');
  final _passwordController = TextEditingController(text: 'password');

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(context.l10n.login)),
      body: Padding(
        padding: EdgeInsets.all(16.w),
        child: BlocConsumer<LoginBloc, LoginState>(
          listenWhen: (prev, curr) => prev.alertState != curr.alertState,
          listener: (context, state) {
            switch (state.alertState) {
              case AlertErrorState():
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(state.submitState.failure.displayMessage),
                  ),
                );
              case AlertDoneState():
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                      'Welcome \${state.submitState.result.user.name}',
                    ),
                  ),
                );
              case _AlertIdleState():
                break;
            }
          },
          builder: (context, state) {
            final isLoading = state.submitState is SubmitLoginLoadingState;
            return Column(
              children: [
                TextField(
                  controller: _emailController,
                  decoration: InputDecoration(labelText: context.l10n.email),
                ),
                12.verticalSpace,
                TextField(
                  controller: _passwordController,
                  obscureText: true,
                  decoration: InputDecoration(
                    labelText: context.l10n.password,
                  ),
                ),
                24.verticalSpace,
                ElevatedButton(
                  onPressed: isLoading
                      ? null
                      : () {
                          context.read<LoginBloc>().add(
                                LoginEvent.submitted(
                                  email: _emailController.text,
                                  password: _passwordController.text,
                                ),
                              );
                        },
                  child: Text(
                    isLoading ? context.l10n.loading : context.l10n.signIn,
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}
EOF

# DI — Injector
cat > lib/injector.dart << 'DART'
import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';
import 'app_router.dart';
import 'injector.config.dart';

final getIt = GetIt.instance;

@InjectableInit()
Future<void> configureDependencies() async {
  getIt.registerLazySingleton<AppRouter>(() => AppRouter());
  getIt.init();
}
DART

# Router
cat > lib/app_router.dart << EOF
import 'package:auto_route/auto_route.dart';
import 'package:${PROJECT_NAME}/features/auth/presentation/pages/login_page.dart';

@AutoRouterConfig(replaceInRouteName: 'Page,Route')
class AppRouter extends RootStackRouter {
  @override
  List<AutoRoute> get routes {
    return [
      AutoRoute(page: LoginRoute.page, initial: true),
    ];
  }
}
EOF

# Main
cat > lib/main.dart << EOF
import 'package:encrypt_shared_preferences/provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:${PROJECT_NAME}/app_router.dart';
import 'package:${PROJECT_NAME}/core/theme/app_theme.dart';
import 'package:${PROJECT_NAME}/gen/l10n/app_localizations.dart';
import 'package:${PROJECT_NAME}/injector.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await EncryptedSharedPreferences.initialize('change_this_key');
  await configureDependencies();

  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
  ]);

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ScreenUtilInit(
      designSize: const Size(390, 844),
      minTextAdapt: true,
      builder: (context, child) {
        return MaterialApp.router(
          title: 'My App',
          debugShowCheckedModeBanner: false,
          theme: AppTheme.lightTheme,
          darkTheme: AppTheme.darkTheme,
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          routerConfig: getIt<AppRouter>().config(),
        );
      },
    );
  }
}
EOF

# Test helpers
cat > test/helpers/test_helpers.dart << DART
import 'package:${PROJECT_NAME}/core/error/failures.dart';
import 'package:${PROJECT_NAME}/core/result/result.dart';

Result<T> tOk<T>(T value) {
  return Result.ok(value);
}

Result<T> tError<T>([String message = 'Something went wrong']) {
  return Result.error(Failure.unexpected(message));
}
DART

# .env
cat > .env << 'EOF'
API_BASE_URL=https://api.example.com
EOF

# .env.example (committed; mirrors .env keys with empty values)
cat > .env.example << 'EOF'
API_BASE_URL=
EOF

# ASSETS — colors.xml (consumed by flutter_gen → lib/gen/colors.gen.dart)
cat > assets/colors/colors.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<resources>
  <!-- Primary -->
  <color name="primary">#1A73E8</color>
  <color name="primary_dark">#1557B0</color>

  <!-- Background -->
  <color name="background_light">#FFFFFF</color>
  <color name="background_dark">#121212</color>
  <color name="surface_dark">#1E1E1E</color>

  <!-- Status -->
  <color name="status_paid">#4CAF50</color>
  <color name="status_due_soon">#FF9800</color>
  <color name="status_overdue">#F44336</color>
  <color name="status_vacant">#9E9E9E</color>

  <!-- Brand -->
  <color name="whatsapp">#1DA851</color>

  <!-- Error -->
  <color name="error">#D32F2F</color>

  <!-- Text -->
  <color name="text_primary_light">#1A1A1A</color>
  <color name="text_secondary_light">#757575</color>
  <color name="text_primary_dark">#FFFFFF</color>
  <color name="text_secondary_dark">#AAAAAA</color>
</resources>
EOF

# ASSETS — sample SVG icons
cat > assets/icons/google_logo.svg << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="24" height="24">
  <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
  <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
  <path fill="#FBBC05" d="M10.53 28.59a14.5 14.5 0 0 1 0-9.18l-7.98-6.19a24.01 24.01 0 0 0 0 21.56l7.98-6.19z"/>
  <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
</svg>
EOF

cat > assets/icons/ic_whatsapp.svg << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">
<g clip-path="url(#clip0_4418_10215)">
<path d="M6.9 20.6C8.4 21.5 10.2 22 12 22C17.5 22 22 17.5 22 12C22 6.5 17.5 2 12 2C6.5 2 2 6.5 2 12C2 13.8 2.5 15.5 3.3 17L2.44044 20.306C2.24572 21.0549 2.93892 21.7317 3.68299 21.5191L6.9 20.6Z" stroke="#fff" stroke-width="1.5" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round" />
<path d="M16.5 14.8485C16.5 15.0105 16.4639 15.177 16.3873 15.339C16.3107 15.501 16.2116 15.654 16.0809 15.798C15.86 16.041 15.6167 16.2165 15.3418 16.329C15.0714 16.4415 14.7784 16.5 14.4629 16.5C14.0033 16.5 13.512 16.392 12.9937 16.1715C12.4755 15.951 11.9572 15.654 11.4434 15.2805C10.9251 14.9025 10.4339 14.484 9.9652 14.0205C9.501 13.5525 9.08187 13.062 8.70781 12.549C8.33826 12.036 8.04081 11.523 7.82449 11.0145C7.60816 10.5015 7.5 10.011 7.5 9.543C7.5 9.237 7.55408 8.9445 7.66224 8.6745C7.77041 8.4 7.94166 8.148 8.18052 7.923C8.46895 7.6395 8.78443 7.5 9.11793 7.5C9.24412 7.5 9.37031 7.527 9.48297 7.581C9.60015 7.635 9.70381 7.716 9.78493 7.833L10.8305 9.3045C10.9116 9.417 10.9702 9.5205 11.0108 9.6195C11.0513 9.714 11.0739 9.8085 11.0739 9.894C11.0739 10.002 11.0423 10.11 10.9792 10.2135C10.9206 10.317 10.835 10.425 10.7268 10.533L10.3843 10.8885C10.3348 10.938 10.3122 10.9965 10.3122 11.0685C10.3122 11.1045 10.3167 11.136 10.3257 11.172C10.3393 11.208 10.3528 11.235 10.3618 11.262C10.4429 11.4105 10.5826 11.604 10.7809 11.838C10.9837 12.072 11.2 12.3105 11.4344 12.549C11.6778 12.7875 11.9121 13.008 12.151 13.2105C12.3853 13.4085 12.5791 13.5435 12.7323 13.6245C12.7549 13.6335 12.7819 13.647 12.8135 13.6605C12.8495 13.674 12.8856 13.6785 12.9261 13.6785C13.0028 13.6785 13.0613 13.6515 13.1109 13.602L13.4534 13.2645C13.5661 13.152 13.6743 13.0665 13.7779 13.0125C13.8816 12.9495 13.9852 12.918 14.0979 12.918C14.1835 12.918 14.2737 12.936 14.3728 12.9765C14.472 13.017 14.5756 13.0755 14.6883 13.152L16.18 14.2095C16.2972 14.2905 16.3783 14.385 16.4279 14.4975C16.473 14.61 16.5 14.7225 16.5 14.8485Z" stroke="#fff" stroke-width="1.5" stroke-miterlimit="10" />
</g>
<defs>
<clipPath id="clip0_4418_10215">
<rect width="24" height="24" fill="white"/>
</clipPath>
</defs>
</svg>
EOF

# ASSETS — keep empty asset dirs in git
touch assets/icons/.gitkeep
touch assets/images/.gitkeep

# RELEASES — bundled launcher icon (referenced by flutter_launcher_icons)
if [ -f "$TEMPLATE_DIR/app_icon_512.png" ]; then
  cp "$TEMPLATE_DIR/app_icon_512.png" releases/app_icon_512.png
else
  echo "⚠️  Template icon missing at $TEMPLATE_DIR/app_icon_512.png — skipping launcher icon copy"
fi

# ========================================
# INSTALL DEPENDENCIES (latest from pub.dev)
# ========================================
echo ""
echo "📡 Installing dependencies (latest versions from pub.dev)..."

echo "  → dependencies..."
pub_add dio freezed_annotation json_annotation get_it injectable auto_route flutter_bloc flutter_screenutil encrypt_shared_preferences envied rxdart intl flutter_svg

echo "  → flutter_localizations from SDK..."
fvm flutter pub add flutter_localizations --sdk=flutter 2>&1 | tail -1

echo "  → dev_dependencies..."
pub_add_dev build_runner freezed json_serializable injectable_generator auto_route_generator envied_generator bloc_test mocktail lint flutter_gen_runner flutter_launcher_icons melos

# --- Drop default flutter_lints (we use lint package instead) ---
if grep -q '^  flutter_lints:' pubspec.yaml; then
  awk '!/^  flutter_lints:/' pubspec.yaml > pubspec.yaml.tmp && mv pubspec.yaml.tmp pubspec.yaml
fi

# --- Replace top-level flutter: block + append flutter_gen / melos / flutter_launcher_icons ---
# `flutter create --empty` writes a minimal `flutter:` block (uses-material-design only) at EOF.
# Strip it (everything from `^flutter:` to EOF) then append the full GM config.
awk '/^flutter:[[:space:]]*$/{exit} {print}' pubspec.yaml > pubspec.yaml.tmp && mv pubspec.yaml.tmp pubspec.yaml

cat >> pubspec.yaml << 'EOF'
flutter_gen:
  output: lib/gen/
  integrations:
    flutter_svg: true
  assets:
    enabled: true
    outputs:
      package_parameter_enabled: false
      class_name: AppAssets
  fonts:
    enabled: true
    outputs:
      class_name: AppFonts
  colors:
    enabled: true
    inputs:
      - assets/colors/colors.xml
    outputs:
      class_name: AppColors

melos:
  sdkPath: .fvm/flutter_sdk
  scripts:
    build:
      run: dart run build_runner build --delete-conflicting-outputs
      description: Generate code (freezed, json_serializable, auto_route, injectable)
    build:watch:
      run: dart run build_runner watch --delete-conflicting-outputs
      description: Watch and regenerate code on file change
    analyze:
      run: flutter analyze
      description: Run Flutter analyzer
    test:
      run: flutter test
      description: Run all unit and widget tests
    test:coverage:
      run: flutter test --coverage
      description: Run tests with coverage report
    format:
      run: dart format lib test
      description: Format all Dart files
    locales:
      run: flutter gen-l10n
      description: Generate localization files from ARB

flutter_launcher_icons:
  android: true
  ios: true
  image_path: "releases/app_icon_512.png"
  min_sdk_android: 21
  adaptive_icon_background: "#2260D3"
  adaptive_icon_foreground: "releases/app_icon_512.png"
  web:
    generate: false

flutter:
  uses-material-design: true
  generate: true

  assets:
    - assets/images/
    - assets/icons/
EOF

# ========================================
# VSCODE CONFIGURATION
# ========================================
echo ""
echo "📁 Creating .vscode configuration..."
mkdir -p .vscode

cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "debug",
            "request": "launch",
            "type": "dart",
            "program": "lib/main.dart"
        },
        {
            "name": "release",
            "request": "launch",
            "type": "dart",
            "program": "lib/main.dart",
            "args": [
                "--release"
            ]
        },
        {
            "name": "profile",
            "request": "launch",
            "type": "dart",
            "program": "lib/main.dart",
            "args": [
                "--profile"
            ]
        }
    ]
}
EOF

cat > .vscode/settings.json << EOF
{
  "dart.flutterSdkPath": ".fvm/versions/${FVM_FLUTTER_VERSION}",
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 0,
  "[dart]": {
    "editor.formatOnSave": true,
    "editor.formatOnType": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "always",
      "source.organizeImports": "always"
    }
  },
  "dart.flutterHotReloadOnSave": "never",
  "dart.lineLength": 80,
  "dart.previewFlutterUiGuides": true,
  "dart.previewFlutterUiGuidesCustomTracking": true,
  "dart.debugExternalPackageLibraries": false,
  "dart.debugSdkLibraries": false,
  "editor.rulers": [80, 120],
  "editor.tabSize": 2,
  "editor.insertSpaces": true,
  "editor.detectIndentation": false,
  "editor.bracketPairColorization.enabled": true,
  "editor.guides.bracketPairs": "active",
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "files.trimFinalNewlines": true,
  "files.exclude": {
    "**/.git": true,
    "**/.DS_Store": true,
    "**/build": false,
    "**/.dart_tool": false,
    "**/.idea": true,
    "**/*.g.dart": false,
    "**/*.freezed.dart": false,
    "**/*.gr.dart": false,
    "**/*.config.dart": false,
    "**/Thumbs.db": true,
    "**/.svn": true,
    "**/.hg": true
  },
  "files.watcherExclude": {
    "**/.git/objects/**": true,
    "**/.git/subtree-cache/**": true,
    "**/build/**": true,
    "**/.dart_tool/**": true
  },
  "search.exclude": {
    "**/build": true,
    "**/.dart_tool": true,
    "**/*.g.dart": true,
    "**/*.freezed.dart": true,
    "**/*.gr.dart": true,
    "**/*.config.dart": true,
    "**/lib/gen/**": true,
    "**/.fvm": true
  },
  "explorer.fileNesting.enabled": true,
  "explorer.fileNesting.expand": false,
  "explorer.fileNesting.patterns": {
    "*.dart": "\${capture}.freezed.dart, \${capture}.g.dart, \${capture}.gr.dart, \${capture}.config.dart",
    "pubspec.yaml": "pubspec.lock, .packages, .flutter-plugins, .flutter-plugins-dependencies, .metadata",
    ".gitignore": ".gitattributes, .gitmodules"
  }
}
EOF

echo ""
echo "✅ Single-module project '$PROJECT_NAME' created!"
echo "   Flutter: $FVM_FLUTTER_VERSION | Dart SDK: $SDK_CONSTRAINT"
echo "   All dependencies resolved to latest versions from pub.dev"
echo ""
echo "Best-practice scaffold included (lib/features/auth/):"
echo "  • Domain  : UserModel, LoginParams, LoginResult, AuthRepository, LoginUseCase, LogoutUseCase"
echo "  • Data    : UserDto, LoginRequest, LoginResponse + separate mapper classes"
echo "             (UserModelMapper, LoginResultMapper, LoginRequestMapper) + AuthRemoteDataSource"
echo "             + AuthRepositoryImpl (with ErrorMapper)"
echo "  • Bloc    : LoginBloc with sub-state union (SubmitLoginState idle/loading/done/error) + AlertState"
echo "  • Page    : LoginPage with init event + BlocConsumer + ScreenUtil"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  fvm flutter pub get                 # also generates AppLocalizations from lib/l10n/*.arb"
echo "  fvm dart run build_runner build --delete-conflicting-outputs"
echo ""
echo "Default login (dummy datasource): demo@example.com / password"
echo ""
