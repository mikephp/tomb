//
//  ViewController.m
//  ThirdIdTest
//
//  Created by dirlt on 15/12/4.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import "ViewController.h"

@interface ViewController ()

@end

@implementation ViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view, typically from a nib.
    [GIDSignIn sharedInstance].uiDelegate = self;
    self.fbButton.readPermissions = @[@"public_profile", @"email"];
    self.fbButton.delegate = self;
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

- (IBAction)didTapSignOut:(id)sender {
    NSLog(@"trigger sign out");
    [[GIDSignIn sharedInstance] disconnect];
}

- (void)loginButtonDidLogOut:(FBSDKLoginButton *)loginButton {
    NSLog(@"facebook logout");
}
- (BOOL)loginButtonWillLogin:(FBSDKLoginButton *)loginButton {
    NSLog(@"facebook will login");
    return YES;
}

- (void)loginButton:(FBSDKLoginButton *)loginButton didCompleteWithResult:(FBSDKLoginManagerLoginResult *)result error:(NSError *)error {
    if (error) {
        NSLog(@"facebook login error = %@", [error localizedDescription]);
    } else if(result.isCancelled) {
        NSLog(@"facebook login cancelled");
    } else {
        FBSDKAccessToken *token = result.token;
        NSLog(@"appid = %@, userid=%@, expire date=%@, token string=%@", token.appID, token.userID, token.expirationDate, token.tokenString);
        
        // send id token to backend server.
        NSString *idToken = token.tokenString;
        NSString *signinEndpoint = @"http://localhost:8082/tokensignin-fb";
        NSDictionary *params = @{@"idtoken": idToken};
        
        NSMutableURLRequest *request = [NSMutableURLRequest requestWithURL:[NSURL URLWithString:signinEndpoint]];
        [request setValue:@"application/x-www-form-urlencoded" forHTTPHeaderField:@"Content-Type"];
        [request setHTTPMethod:@"POST"];
        [request setHTTPBody:[NSJSONSerialization dataWithJSONObject:params options:0 error:nil]];
        
        NSOperationQueue *queue = [[NSOperationQueue alloc] init];
        [NSURLConnection sendAsynchronousRequest:request
                                           queue:queue
                               completionHandler:^(NSURLResponse *response, NSData *data, NSError *error) {
                                   if (error) {
                                       NSLog(@"Error: %@", error.localizedDescription);
                                   } else {
                                       NSLog(@"Request OK. response = %@", [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding]);
                                   }
                               }];
    }
}

@end
