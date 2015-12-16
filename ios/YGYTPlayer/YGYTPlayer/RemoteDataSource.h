//
//  RemoteDataSource.h
//  
//
//  Created by dirlt on 15/11/12.
//
//

#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>

@interface RemoteDataSource : NSObject
+ (RemoteDataSource*) getInstance;
@property (assign) NSTimeInterval timeout;
@property (nonatomic, strong) UIImage *placeholderImage;

// remote data.
typedef void (^fetchDataComplete)(NSString *key, NSDictionary *json);
- (void) fetchData: (NSString *)key withExpireInterval:(NSInteger)expireInterval withComplete: (fetchDataComplete) complete;
- (void) fetchDataWithoutCache: (NSString *)key withComplete: (fetchDataComplete) complete;

// bookmark data.
- (void) saveBookMark: (NSString*) key withContent: (NSDictionary*) json withValue: (NSInteger) v;
typedef void (^loadBookMarkComplete)(NSString* key, NSInteger mark);
- (void) loadBookMark: (NSString*) key withComplete: (loadBookMarkComplete)complete;
- (void) removeBookMark: (NSString*) key;
typedef void (^loadAllBookMarkComplete)(NSMutableArray *array);
- (void) loadAllBookMark: (loadAllBookMarkComplete) complete;

// history data.
- (void) saveHistory: (NSString*) key withContent: (NSDictionary*) json withElapse: (NSInteger) elapse;
typedef void (^loadHistoryComplete)(NSString* key, NSInteger elapse);
- (void) loadHistory: (NSString*) key withComplete: (loadHistoryComplete) complete;
- (void) removeHistory: (NSString*) key;
typedef void (^loadAllHistoryComplete)(NSMutableArray *array);
- (void) loadAllHistory: (loadAllHistoryComplete) complete;

// settings data.
- (void) saveSettings: (NSString*) key withData: (NSDictionary*) json;
// sync way.
- (NSDictionary*) loadSettings: (NSString*) key withDefaultData: (NSDictionary*) json;

// search history term.
typedef void (^loadSearchHistoryComplete)(NSMutableArray *array);
- (void) loadSearchHistory: (NSInteger) limit withComplete:(loadSearchHistoryComplete) complete;
- (void) saveSearchHistory: (NSString*) term;
- (void) removeSearchHistory: (NSString*) term;

@end
