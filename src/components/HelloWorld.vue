<template>
    <div class="layout">
        <Layout>
            <Header>
                <Menu mode="horizontal" theme="dark" active-name="1" @on-select="onMenuSelect">
                    <div class="layout-nav">
                        <MenuItem name="tool">
                            <Icon type="ios-navigate"></Icon>
                            Carbon Tool
                        </MenuItem>
                        <MenuItem name="userguide">
                            <Icon type="ios-keypad"></Icon>
                            User Guide
                        </MenuItem>
                        <MenuItem name="resource">
                            <Icon type="ios-analytics"></Icon>
                            Resources
                        </MenuItem>
                        <MenuItem name="4">
                            <Icon type="ios-paper"></Icon>
                            Contact Us
                        </MenuItem>
                    </div>
                </Menu>
            </Header>
            <Content :style="{padding: '0 50px'}">
            </Content>
            <Footer class="layout-footer-center">2022 &copy; Arup China Building Central</Footer>
        </Layout>
    </div>
</template>
<style scoped>
.layout{
    border: 1px solid #d7dde4;
    background: #f5f7f9;
    position: relative;
    border-radius: 4px;
    overflow: hidden;
}
.layout-nav{
    width: 550px;
    margin: 0 auto;
    margin-right: 20px;
}
.layout-footer-center{
    text-align: center;
}
</style>
<script>
export default {
    data () {
        return {
          books: [],
        }
    },
    methods: {
        onMenuSelect(name) {
            if (name === "tool") {
              this.$router.push("/");
            } else {
              this.$router.push(name);
            }
        },
    }

}
</script>
