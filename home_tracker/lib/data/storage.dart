import '../models/models.dart';
import 'firestore_service.dart';

class Storage {
  static String genId() => FirestoreService.genId();

  static Future<List<String>> loadCategories() => FirestoreService.loadCategories();
  static Future<void> saveCategories(List<String> cats) => FirestoreService.saveCategories(cats);

  static Future<List<Chore>> loadChores() => FirestoreService.loadChores();
  static Future<void> saveChores(List<Chore> chores) => FirestoreService.saveChores(chores);

  static Future<List<Purchase>> loadPurchases() => FirestoreService.loadPurchases();
  static Future<void> savePurchases(List<Purchase> purchases) => FirestoreService.savePurchases(purchases);

  static Future<List<FamilyEvent>> loadEvents() => FirestoreService.loadEvents();
  static Future<void> saveEvents(List<FamilyEvent> events) => FirestoreService.saveEvents(events);
}
