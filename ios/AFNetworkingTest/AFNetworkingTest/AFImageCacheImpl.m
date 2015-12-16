//
//  AFImageCacheImpl.m
//  Pods
//
//  Created by dirlt on 15/11/11.
//
//

#import "AFImageCacheImpl.h"
#include <CommonCrypto/CommonDigest.h>
#import <UIImage+WebP.h>

@interface AFImageCacheImpl ()
@property (nonatomic, strong) NSString *docRoot;
@property (nonatomic, strong) NSString *imageRoot;
@property (nonatomic, weak) NSFileManager *fm;
@end

@implementation AFImageCacheImpl

- (id) init {
    self = [super init];
    if (!self) return nil;
    NSArray *paths = NSSearchPathForDirectoriesInDomains
    (NSDocumentDirectory, NSUserDomainMask, YES);
    self.docRoot = [paths objectAtIndex:0];
    self.imageRoot = [NSString stringWithFormat:@"%@/images/", self.docRoot];
    self.fm = [NSFileManager defaultManager];
    [self.fm createDirectoryAtPath:self.imageRoot withIntermediateDirectories:YES attributes:nil error:nil];
    return self;
}

static inline NSString* imageCacheKeyFromURLRequest(NSURLRequest *request) {
    NSString* path = [request.URL path];
    NSData *data = [path dataUsingEncoding:NSUTF8StringEncoding];
    uint8_t digest[CC_SHA1_DIGEST_LENGTH];
    CC_SHA1(data.bytes, (CC_LONG)data.length, digest);
    NSMutableString *output = [NSMutableString stringWithCapacity:CC_SHA1_DIGEST_LENGTH * 2];
    for (int i = 0; i < CC_SHA1_DIGEST_LENGTH; i++) {
        [output appendFormat:@"%02x", digest[i]];
    }
    // NSLog(@"imageCacheKey path = %@, key = %@", path, output);
    return output;
}

static const BOOL MEMORY_CACHE = NO;
static const BOOL FS_CACHE = YES;

- (UIImage *)cachedImageForRequest:(NSURLRequest *)request {
    switch ([request cachePolicy]) {
        case NSURLRequestReloadIgnoringCacheData:
        case NSURLRequestReloadIgnoringLocalAndRemoteCacheData:
            return nil;
        default:
            break;
    }
    NSString *key = imageCacheKeyFromURLRequest(request);
    NSLog(@"request image, key = %@", key);
    if (MEMORY_CACHE) {
        UIImage *cache = [self objectForKey:key];
        if (cache) {
            NSLog(@"image found in memory. key = %@", key);
            return cache;
        }
    }
    if (FS_CACHE) {
        NSString *fname = [self.imageRoot stringByAppendingString:key];
        if ([self.fm fileExistsAtPath:fname]) {
            NSLog(@"image found on fs. key = %@", key);
            // return [UIImage imageWithWebP:fname];
            return [UIImage imageNamed:fname];
        }
    }
    return nil;
}

- (void)cacheImage:(UIImage *)image
        forRequest:(NSURLRequest *)request
{
    if (!image || !request) return;
    NSString *key = imageCacheKeyFromURLRequest(request);
    if (MEMORY_CACHE) {
        NSLog(@"cache image in memory, key = %@", key);
        [self setObject:image forKey:key];
    }
    if (FS_CACHE) {
        NSString *fname = [self.imageRoot stringByAppendingString:key];
        if (![self.fm fileExistsAtPath:fname]) {
            // NSData *data = UIImagePNGRepresentation(image);
            NSData *data = [UIImage imageToWebP:image quality:1.0];
            if (![data writeToFile:fname atomically:YES]) {
                NSLog(@"cache image on fs failed. key = %@", key);
            } else {
                NSLog(@"cache image on fs OK. key = %@", key);
            }
        }
    }
    return;
}
@end
