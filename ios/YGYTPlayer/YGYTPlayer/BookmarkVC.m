//
//  BookmarkVC.m
//  YGYTPlayer
//
//  Created by dirlt on 15/11/13.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import "BookmarkVC.h"
#import "PlayListCell.h"
#import "RemoteDataSource.h"
#import "VideoVC.h"
#import "HintCell.h"

@implementation BookmarkVC

- (void)viewDidLoad {
    [super viewDidLoad];
    
    // Uncomment the following line to preserve selection between presentations.
    // self.clearsSelectionOnViewWillAppear = NO;
    
    // Uncomment the following line to display an Edit button in the navigation bar for this view controller.
    // self.navigationItem.rightBarButtonItem = self.editButtonItem;
    [PlayListCell configureTableView:self.tableView];
    self.array = [[NSMutableArray alloc] init];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

- (void)reloadData {
    RemoteDataSource *rds = [RemoteDataSource getInstance];
    __weak BookmarkVC* me = self;
    [rds loadAllBookMark:^(NSMutableArray *array) {
        me.array = array;
        [me.tableView reloadData];
    }];
}

- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];
    self.parentViewController.navigationItem.title = @"BOOKMARKS";
    self.parentViewController.navigationItem.rightBarButtonItem = nil;
    self.parentViewController.navigationItem.leftBarButtonItem = nil;
    [self reloadData];
}
#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
// #warning Incomplete implementation, return the number of sections
    return 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
// #warning Incomplete implementation, return the number of rows
    if (self.array.count == 0) return 1;
    return self.array.count;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    if (self.array.count == 0) {
        HintCell *cell = [HintCell getInstance];
        [cell setHintText:@"No Bookmarks"];
        return cell;
    }
    PlayListCell *cell = [PlayListCell fetchCell:self.tableView];
    NSDictionary *json = self.array[indexPath.row];
    [cell fillWithDictionary:json withCellKind:CELL_KIND_BOOKMARK];
    return cell;
}

// Override to support conditional editing of the table view.
- (BOOL)tableView:(UITableView *)tableView canEditRowAtIndexPath:(NSIndexPath *)indexPath {
    // Return NO if you do not want the specified item to be editable.
    if (self.array.count == 0) {
        return NO;
    }
    return YES;
}

// Override to support editing the table view.
- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath {
    if (editingStyle == UITableViewCellEditingStyleDelete) {
        // Delete the row from the data source
        NSDictionary *json = self.array[indexPath.row];
        [self.array removeObjectAtIndex:indexPath.row];
        [[RemoteDataSource getInstance] removeBookMark:json[@"id"]];
        // [tableView deleteRowsAtIndexPaths:@[indexPath] withRowAnimation:UITableViewRowAnimationFade];
        [tableView reloadData];
    } else if (editingStyle == UITableViewCellEditingStyleInsert) {
        // Create a new instance of the appropriate class, insert it into the array, and add a new row to the table view
    }   
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    if (self.array.count == 0) return;
    VideoVC *vc = [VideoVC getInstance];
    [vc loadData:self.array[indexPath.row]];
    [self.navigationController pushViewController:vc animated:YES];
}

/*
// Override to support rearranging the table view.
- (void)tableView:(UITableView *)tableView moveRowAtIndexPath:(NSIndexPath *)fromIndexPath toIndexPath:(NSIndexPath *)toIndexPath {
}
*/

/*
// Override to support conditional rearranging of the table view.
- (BOOL)tableView:(UITableView *)tableView canMoveRowAtIndexPath:(NSIndexPath *)indexPath {
    // Return NO if you do not want the item to be re-orderable.
    return YES;
}
*/

/*
#pragma mark - Navigation

// In a storyboard-based application, you will often want to do a little preparation before navigation
- (void)prepareForSegue:(UIStoryboardSegue *)segue sender:(id)sender {
    // Get the new view controller using [segue destinationViewController].
    // Pass the selected object to the new view controller.
}
*/

@end
