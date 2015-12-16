//
//  VideoVC.m
//  YGYTPlayer
//
//  Created by dirlt on 15/11/12.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import "VideoVC.h"
#import <AVFoundation/AVFoundation.h>
#import <AVKit/AVKit.h>
#import <AFNetworking/UIImageView+AFNetworking.h>
#import "PlayListCell.h"
#import "RemoteDataSource.h"
#import "VideoCell.h"
#import "PlayerVC.h"

@interface VideoVC ()


@end

@implementation VideoVC

static VideoVC* instance = nil;

+ (id)getInstance {
    if (instance) return instance;
    // instance = [[VideoVC alloc] initWithNibName:@"VideoVC" bundle:nil];
    UIStoryboard *sb = [UIStoryboard storyboardWithName:@"Main" bundle:[NSBundle mainBundle]];
    instance = (VideoVC*) [sb instantiateViewControllerWithIdentifier:@"VideoVC"];
    return instance;
}

- (void)viewDidLoad {
    [super viewDidLoad];
}

- (void)loadData: (NSDictionary*) json {
    self.json = json;
    self.navigationItem.title = @"DETAIL";
    // Do any additional setup after loading the view.
//    NSLog(@"videovc load. video id = %@, title = %@, desc = %@, im = %@, views = %@",
//          self.json[@"id"], self.json[@"tt"], self.json[@"desc"], self.json[@"im"],
//          self.json[@"views"]);
    self.header = [VideoCell getInstance];
    [self.header fillCell:self.json];
    self.videos = nil;
    [self.tableView reloadData];
    NSString *key = [NSString stringWithFormat:@"detail/?id=%@",self.json[@"id"]];
    [[RemoteDataSource getInstance] fetchData:key withExpireInterval: 3600 * 24 * 30 withComplete:^(NSString *key, NSDictionary *json) {
        if(!json) return;
        // NSLog(@"request complete. key = %@, json = %@", key, json);
        self.videos = (NSArray*)json[@"vds"];
        [self.tableView reloadData];
    }];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    return 2;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    if (section == 0) {
        return 1;
    } else {
        if (self.videos) return self.videos.count;
        return 0;
    }
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section {
//    if (section == 1) {
//        return @" ";
//    }
    return nil;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    if(indexPath.section == 0) {
        return self.header;
    } else {
        PlayListCell *cell = [PlayListCell fetchCell:tableView];
        [cell fillWithDictionary:self.videos[indexPath.row] withCellKind:CELL_KIND_VIDEO];
        return cell;
    }
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    if (indexPath.section == 1) {
        return PLAY_LIST_CELL_HEIGHT;
    } else {
        CGFloat width = self.tableView.frame.size.width;
        return [self.header rowHeight:width];
    }
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    if (indexPath.section == 1) {
        NSDictionary* json = self.videos[indexPath.row];
        PlayerVC *vc = [PlayerVC getInstance];
        [vc loadData:json];
        [self.navigationController pushViewController:vc animated:YES];
    }
}

//- (CGFloat)tableView:(UITableView *)tableView estimatedHeightForRowAtIndexPath:(nonnull NSIndexPath *)indexPath {
//    if (indexPath.section == 1) {
//        return 100.0;
//    } else {
//        return [self.header rowHeight];
//    }
//}

/*
#pragma mark - Navigation

// In a storyboard-based application, you will often want to do a little preparation before navigation
- (void)prepareForSegue:(UIStoryboardSegue *)segue sender:(id)sender {
    // Get the new view controller using [segue destinationViewController].
    // Pass the selected object to the new view controller.
}
*/

@end
