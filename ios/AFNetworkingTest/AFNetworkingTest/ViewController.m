//
//  ViewController.m
//  AFNetworkingTest
//
//  Created by dirlt on 15/11/11.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import "ViewController.h"
#import <AFNetworking/AFNetworking.h>
#import <AFNetworking/UIImageView+AFNetworking.h>
#import <AFNetworking/UIActivityIndicatorView+AFNetworking.h>

@interface ViewController ()
@property (weak, nonatomic) IBOutlet UIImageView *imageView;
@property (weak, nonatomic) IBOutlet UIActivityIndicatorView *jsonIndicator;
@property (weak, nonatomic) IBOutlet UIActivityIndicatorView *imageIndicator;
@end

@implementation ViewController
static NSString * const BaseURLString = @"http://www.raywenderlich.com/demos/weather_sample/";

- (void)viewDidLoad {
    [super viewDidLoad];
    self.jsonIndicator.hidden = YES;
    self.imageIndicator.hidden = YES;
    // Do any additional setup after loading the view, typically from a nib.
}
- (IBAction)jsonTapped:(id)sender {
    NSString *string = [NSString stringWithFormat:@"%@weather.php?format=json", BaseURLString];
    // NSString *string = @"http://localhost:10001/index.json";
    NSURL *url = [NSURL URLWithString:string];
    NSURLRequest *request = [NSURLRequest requestWithURL: url];
    
    __weak ViewController *me = self;
    AFHTTPRequestOperation *operation = [[AFHTTPRequestOperation alloc] initWithRequest:request];
    operation.responseSerializer = [AFJSONResponseSerializer serializer];
    self.jsonIndicator.hidden = NO;
    [self.jsonIndicator startAnimating];
    [operation setCompletionBlockWithSuccess:^(AFHTTPRequestOperation *operation, id responseObject) {
        // NSLog(@"got json response = %@", [(NSDictionary*) responseObject description]);
        NSLog(@"got json response");
        [self.jsonIndicator stopAnimating];
        self.jsonIndicator.hidden = YES;
    } failure:^(AFHTTPRequestOperation *operation, NSError *error) {
        // sample code of AlterView.
//        UIAlertView *alertView = [[UIAlertView alloc] initWithTitle:@"Error Retrieving"
//                                                            message:[error localizedDescription]
//                                                           delegate:nil
//                                                  cancelButtonTitle:@"Ok"
//                                                  otherButtonTitles:nil];
//        [alertView show];
        [self.jsonIndicator stopAnimating];
        self.jsonIndicator.hidden = YES;
        NSLog(@"got json failed. error = %@", [error localizedDescription]);
    }];
    [operation start];
    // [self.jsonIndicator setAnimatingWithStateOfOperation:operation];
}

- (IBAction)imageTapped:(id)sender {
    // NSString *imageURL = @"http://www.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0008_clear_sky_night.png";
    NSString *imageURL = @"https://i.ytimg.com/vi_webp/oBu-pQG6sTY/mqdefault.webp";
    NSURL *url = [NSURL URLWithString:imageURL];
    NSURLRequest *request = [NSURLRequest requestWithURL: url];
    self.imageIndicator.hidden = NO;
    [self.imageIndicator startAnimating];
    __weak ViewController *me = self;
    [self.imageView setImageWithURLRequest:request placeholderImage:nil success:^(NSURLRequest * _Nonnull request, NSHTTPURLResponse * _Nullable response, UIImage * _Nonnull image) {
        self.imageIndicator.hidden = YES;
        [self.imageIndicator stopAnimating];
        me.imageView.image = image;
        NSLog(@"image view load OK");
    } failure:^(NSURLRequest * _Nonnull request, NSHTTPURLResponse * _Nullable response, NSError * _Nonnull error) {
        NSLog(@"image view load failed, error = %@", error);
        self.imageIndicator.hidden = YES;
        [self.imageIndicator stopAnimating];
    }];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

@end
