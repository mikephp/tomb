//
//  RemoteDataSource.m
//  
//
//  Created by dirlt on 15/11/12.
//
//

#import "RemoteDataSource.h"
#import <FMDB/FMDB.h>
#import <AFNetworking/AFNetworking.h>
#import <CommonCrypto/CommonDigest.h>

@interface RemoteDataSource ()
@property (nonatomic, strong) FMDatabase *db;
@property (nonatomic, strong) FMDatabaseQueue *dbQueue;
@end

@implementation RemoteDataSource

+ (RemoteDataSource*) getInstance {
    static RemoteDataSource *_instance = nil;
    if (!_instance) {
        _instance = [[RemoteDataSource alloc] init];
        _instance.timeout = 3;
    }
    return _instance;
}

- (void) feedPresentData {
    [self fetchData:@"index/?s=0&c=20&lang=0" withExpireInterval:60 withComplete:^(NSString *key, NSDictionary *json) {
        NSArray *vds = json[@"vds"];
        [vds enumerateObjectsUsingBlock:^(id  _Nonnull obj, NSUInteger idx, BOOL * _Nonnull stop) {
            NSDictionary *js = obj;
            [self saveBookMark:js[@"key"] withContent:js withValue:1];
        }];
    }];
    [self fetchData:@"detail/?id=TXU591OYOHA" withExpireInterval:60 withComplete:^(NSString *key, NSDictionary *json) {
        NSArray *vds = json[@"vds"];
        [vds enumerateObjectsUsingBlock:^(id  _Nonnull obj, NSUInteger idx, BOOL * _Nonnull stop) {
            NSDictionary *js = obj;
            [self saveHistory:js[@"key"] withContent:js withElapse:10];
        }];
    }];
}

static const BOOL CLEAN_ENV = YES;
- (id) init {
    self = [super init];
    if (!self) return nil;
    // prepare database.
    NSArray *paths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
    NSString *appRoot = [paths objectAtIndex:0];
    NSString *dbPath = [NSString stringWithFormat:@"%@/db.sqlite3", appRoot];
    self.db = [FMDatabase databaseWithPath:dbPath];
    [self.db open];
    if (CLEAN_ENV) {
        [self.db executeUpdate:@"DROP TABLE IF EXISTS cache"];
        [self.db executeUpdate:@"DROP TABLE IF EXISTS settings"];
        [self.db executeUpdate:@"DROP TABLE IF EXISTS bookmark"];
        [self.db executeUpdate:@"DROP TABLE IF EXISTS history"];
    }
    if (![self.db executeUpdate:@"CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, content BLOB, expire INTEGER);"]) {
        NSLog(@"create table cache error = %@",self.db.lastError.localizedDescription);
    }
    if (![self.db executeUpdate:@"CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, content BLOB);"]) {
        NSLog(@"create table settings error = %@", self.db.lastError.localizedDescription);
    }
    if (![self.db executeUpdate:@"CREATE TABLE IF NOT EXISTS bookmark (key TEXT PRIMARY KEY, content BLOB, mark INTEGER, ts INTEGER);"]) {
        NSLog(@"create table bookmark error = %@", self.db.lastError.localizedDescription);
    }
    if (![self.db executeUpdate:@"CREATE TABLE IF NOT EXISTS history (key TEXT PRIMARY KEY, content BLOB, elapse INTEGER, ts INTEGER);"]) {
        NSLog(@"create table history error = %@", self.db.lastError.localizedDescription);
    }
    if (![self.db executeUpdate:@"CREATE TABLE IF NOT EXISTS SearchHistory (term TEXT PRIMARY KEY, ts INTEGER);"]) {
        NSLog(@"create table search history error = %@", self.db.lastError.localizedDescription);
    }
    NSInteger now = (NSInteger)[NSDate timeIntervalSinceReferenceDate];
    [self.db executeUpdate:@"DELETE FROM cache WHERE expire < ?", [NSNumber numberWithInteger:now]];
    [self.db executeUpdate:@"DELETE FROM bookmark WHERE mark = 0"];
    [self.db executeUpdate:@"DELETE FROM history WHERE elapse = 0"];
    // [self dbTest]; // some test.
    [self.db close];
    // use FMDBQueue in practice.
    self.dbQueue = [FMDatabaseQueue databaseQueueWithPath:dbPath];
    self.placeholderImage = [UIImage imageNamed:@"placeholder"];
    // [self feedPresentData];
    return self;
}

static inline NSData* jsonToData(NSDictionary *json) {
    return [NSJSONSerialization dataWithJSONObject:json options:0 error:nil];
}
static inline NSDictionary* dataToJson(NSData *data) {
    return [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
}

///////////////// http request /////////////
// static const NSString *URL_PREFIX = @"http://localhost:10001/";
static const NSString *URL_PREFIX=@"http://ygyt.yogamonkey.fit/";

static NSURLRequest* constructURLRequest(NSString *key) {
    NSString *string = [URL_PREFIX stringByAppendingString:key];
    NSURL *url = [NSURL URLWithString:string];
    NSURLRequest *req = [NSURLRequest requestWithURL: url];
    return req;
}

- (void) fetchDataWithoutCache: (NSString *)key withComplete: (fetchDataComplete) complete {
    NSURLRequest *request = constructURLRequest(key);
    // NSLog(@"http op url = %@", request.URL);
    AFHTTPRequestOperation *operation = [[AFHTTPRequestOperation alloc] initWithRequest:request];
    operation.responseSerializer = [AFJSONResponseSerializer serializer];
    [operation setCompletionBlockWithSuccess:^(AFHTTPRequestOperation *operation, id responseObject) {
        // NSLog(@"http complete, response = %@", responseObject);
        NSDictionary *json = (NSDictionary*) responseObject;
        complete(key, json);
    } failure:^(AFHTTPRequestOperation *operation, NSError *error) {
        NSLog(@"http failed. error = %@", error.localizedDescription);
        complete(key, nil);
    }];
    [operation start];
}

- (void) fetchData: (NSString *)key withExpireInterval: (NSInteger)expireInterval withComplete: (fetchDataComplete) complete {
    [self.dbQueue inDatabase:^(FMDatabase* db) {
        FMResultSet *res = [db executeQuery:@"SELECT * FROM cache WHERE key = ?", key];
        BOOL doHttp = YES;
        // NSLog(@"db op: select * from cache where key = %@", key);
        if ([res next]) {
            NSData *content = [res dataForColumn:@"content"];
            NSInteger expire = [res intForColumn:@"expire"];
            NSInteger now = (NSInteger)[NSDate timeIntervalSinceReferenceDate];
            // to suppress warning.
            while ([res next]) { ; }
            if (expire < now) {
                doHttp = YES;
            } else {
                NSLog(@"db op: yeah! cached. key = %@", key);
                doHttp = NO;
                NSDictionary* json = dataToJson(content);
                complete(key, json);
                return ;
            }
        } else {
            doHttp = YES;
        }
        assert(doHttp == YES);
        NSURLRequest *request = constructURLRequest(key);
        // NSLog(@"http op url = %@", request.URL);
        AFHTTPRequestOperation *operation = [[AFHTTPRequestOperation alloc] initWithRequest:request];
        operation.responseSerializer = [AFJSONResponseSerializer serializer];
        __weak RemoteDataSource *me = self;
        [operation setCompletionBlockWithSuccess:^(AFHTTPRequestOperation *operation, id responseObject) {
            NSDictionary *json = (NSDictionary*) responseObject;
            NSData *data = jsonToData(json);
            // cache it.
            [me.dbQueue inDatabase:^(FMDatabase *db) {
                NSInteger now = (NSInteger)[NSDate timeIntervalSinceReferenceDate];
                NSInteger expire = now + expireInterval;
                BOOL ok = [db executeUpdate:@"INSERT OR REPLACE INTO cache VALUES(?, ?, ?)", key, data, [NSNumber numberWithInteger:expire]];
                if (!ok) {
                    NSLog(@"update cache failed");
                }
            }];
            complete(key, json);
        } failure:^(AFHTTPRequestOperation *operation, NSError *error) {
            complete(key, nil);
        }];
        [operation start];
    }];
}

////////////////// bookmark ////////////////

- (void) saveBookMark: (NSString*) key withContent: (NSDictionary*) json withValue: (NSInteger) v {
    [self.dbQueue inDatabase:^(FMDatabase *db) {
        NSData *data = jsonToData(json);
        NSInteger ts = (NSInteger)[NSDate timeIntervalSinceReferenceDate];
        if (![db executeUpdate:@"INSERT OR REPLACE INTO bookmark VALUES(?,?,?,?);", key, data, [NSNumber numberWithInteger:v], [NSNumber numberWithInteger:ts]]) {
            NSLog(@"save bookmark failed");
        }
    }];
}

- (void) loadBookMark: (NSString*) key withComplete: (loadBookMarkComplete)complete {
    [self.dbQueue inDatabase:^(FMDatabase *db) {
        FMResultSet *res = [db executeQuery:@"SELECT mark FROM bookmark WHERE key = ?", key];
        NSInteger mark = 0;
        if ([res next]) {
            mark = [res intForColumn:@"mark"];
            while ([res next]) {;}
        }
        complete(key, mark);
    }];
}

- (void) removeBookMark: (NSString*) key {
    [self.dbQueue inDatabase:^(FMDatabase *db) {
        if (![db executeUpdate:@"UPDATE bookmark SET mark = 0 WHERE key = ?", key]) {
            NSLog(@"remove bookmark failed");
        }
    }];
}

- (void) loadAllBookMark: (loadAllBookMarkComplete) complete {
    NSMutableArray *array = [[NSMutableArray alloc] init];
    [self.dbQueue inDatabase:^(FMDatabase *db) {
        FMResultSet *res = [db executeQuery:@"SELECT content FROM bookmark WHERE mark = 1 ORDER BY ts DESC;"];
        while([res next]) {
            NSData *data = [res dataForColumn:@"content"];
            NSDictionary* json = dataToJson(data);
            [array addObject:json];
        }
        complete(array);
    }];
}

/////////////////// history //////////////////

- (void) saveHistory: (NSString*) key withContent: (NSDictionary*) json withElapse: (NSInteger) elapse {
    [self.dbQueue inDatabase:^(FMDatabase *db) {
        NSData *data = jsonToData(json);
        NSInteger ts = (NSInteger)[NSDate timeIntervalSinceReferenceDate];
        if (![db executeUpdate:@"INSERT OR REPLACE INTO history VALUES(?, ?, ?, ?);", key, data, [NSNumber numberWithInteger:elapse], [NSNumber numberWithInteger:ts]]) {
            NSLog(@"save history failed");
        }
    }];
}

- (void) loadHistory:(NSString *)key withComplete:(loadHistoryComplete)complete {
    [self.dbQueue inDatabase:^(FMDatabase *db) {
        FMResultSet *res = [db executeQuery:@"SELECT elapse FROM history WHERE key = ?", key];
        NSInteger elapse = 0;
        if ([res next]) {
            elapse = [res intForColumn:@"elapse"];
            while ([res next]) {;}
        }
        complete(key, elapse);
    }];
}

- (void) removeHistory: (NSString*) key {
    [self.dbQueue inDatabase:^(FMDatabase *db) {
        if (![db executeUpdate:@"UPDATE history SET elapse = 0 WHERE key = ?", key]) {
            NSLog(@"remove history failed");
        }
    }];
}

- (void) loadAllHistory: (loadAllHistoryComplete) complete {
    NSMutableArray *array = [[NSMutableArray alloc] init];
    [self.dbQueue inDatabase:^(FMDatabase *db) {
        FMResultSet *res = [db executeQuery:@"SELECT content FROM history WHERE elapse != 0 ORDER BY ts DESC;"];
        while([res next]) {
            NSData *data = [res dataForColumn:@"content"];
            NSDictionary* json = dataToJson(data);
            [array addObject:json];
        }
        complete(array);
    }];
}

/////////////////// settings ////////////////

- (void) saveSettings: (NSString*) key withData: (NSDictionary*) json {
    [self.dbQueue inDatabase:^(FMDatabase *db) {
        NSData *data = jsonToData(json);
        if (![db executeUpdate:@"INSERT OR REPLACE INTO settings VALUES(?, ?)", key, data]) {
            NSLog(@"save settings failed");
        }
    }];
}
- (NSDictionary*) loadSettings: (NSString*) key withDefaultData: (NSDictionary*) json {
    FMResultSet *res = [self.db executeQuery:@"SELECT content FROM settings WHERE key = ?", key];
    if ([res next]) {
        NSData *data = [res dataForColumn:@"content"];
        NSDictionary *json2 = dataToJson(data);
        while([res next]) {;}
        return json2;
    }
    return json;
}

//// search history ////
- (void) loadSearchHistory:(NSInteger)limit withComplete:(loadSearchHistoryComplete)complete {
    [self.dbQueue inDatabase:^(FMDatabase *db) {
        FMResultSet *res = [db executeQuery:@"SELECT term FROM SearchHistory ORDER BY ts DESC LIMIT 10;"];
        NSMutableArray *array = [[NSMutableArray alloc] init];
        while ([res next]) {
            NSString *term = [res stringForColumn:@"term"];
            [array addObject:term];
        }
        complete(array);
    }];
}
- (void) saveSearchHistory:(NSString *)term {
    [self.dbQueue inDatabase:^(FMDatabase *db) {
        NSInteger now = (NSInteger)[NSDate timeIntervalSinceReferenceDate];
        if (![db executeUpdate:@"INSERT OR REPLACE INTO SearchHistory VALUES(?, ?);", term, [NSNumber numberWithInteger:now]]) {
            NSLog(@"save search history failed");
        }
    }];
}
- (void) removeSearchHistory:(NSString *)term {
    [self.dbQueue inDatabase:^(FMDatabase *db) {
        if (![db executeUpdate:@"DELETE FROM SearchHistory WHERE term = ?", term]) {
            NSLog(@"delete from search history failed");
        }
    }];
}

@end
